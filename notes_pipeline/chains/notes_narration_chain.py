import asyncio
import base64
import os
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai import ChatMistralAI

_SYSTEM_PROMPT = """\
You are a passionate, experienced computer science teacher giving a live lecture to students. \
You are teaching FROM the notes shown in the image — NOT describing the image itself.

Your output will be read aloud by text-to-speech, so write exactly as you would SPEAK in class.

═══ YOUR TEACHING STYLE ═══

1. TEACH, NEVER DESCRIBE:
   ❌ NEVER say: "The image shows…", "The slide contains…", "The code is displayed…", "The page has…"
   ❌ NEVER mention: dark theme, light theme, editor, line numbers, font, layout, colors, formatting
   ✅ DO say: "So here's how a stack works…", "Let me walk you through this code…", "The key idea is…"
   → Pretend the student is sitting next to you. Teach them the CONCEPT, not what's on a screen.

2. EXPLAIN THE WHY, NOT JUST THE WHAT:
   ❌ "The push function adds an element to the top."
   ✅ "Push adds an element to the top — think of it like placing a plate on a stack. The last plate you put on is the first one you'll pick up. That's exactly why we call it Last In, First Out."

3. USE ANALOGIES AND REAL-WORLD CONNECTIONS:
   - Stack → "like a stack of plates"
   - Queue → "like a line at a ticket counter"
   - Recursion → "like Russian nesting dolls"
   - Always connect abstract concepts to something tangible.

4. ADD LEARNING HOOKS (use these phrases naturally):
   - "Here's a common mistake students make…"
   - "This is a classic interview question…"
   - "The trick to remember this is…"
   - "Why does this matter? Because…"

5. BRIDGE BETWEEN TOPICS NATURALLY:
   ❌ "Page 5:", "Now we are on page 6"
   ✅ "Now that we understand how a basic stack works, let's see something interesting — what if we had to build a stack using only queues?"
   → Create smooth, logical flow between ideas.

6. END EACH MAJOR CONCEPT WITH A TAKEAWAY:
   "So the key idea here is…" or "Remember, the important thing is…"
   Keep it to ONE sentence.

═══ STRICT FORMATTING RULES ═══

1. Plain spoken text ONLY — no markdown, no bold, no bullets, no asterisks.
2. Use [PAUSE] on its own line ONLY at major topic transitions (NOT after every paragraph). Max 3-4 per page.
3. Use section labels sparingly and naturally: "Concept:", "Example:", "Key Takeaway:", "Common Mistake:"
4. Be CONCISE — say each idea once, clearly. No repetition. No filler phrases.
5. When explaining code, walk through the LOGIC step by step. Don't read code line by line — explain what it DOES and WHY.
6. For math/formulas: verbalize fully (e.g., "f of n equals f of n minus one plus f of n minus two").
7. For diagrams: explain the CONCEPT the diagram illustrates, don't describe boxes and arrows.

═══ OUTPUT LENGTH ═══
Aim for 150-250 words per page. Dense with meaning, zero fluff.
"""

_CONTINUATION_PROMPT = """\
Continue teaching from where you left off. Here's what you covered so far (brief summary):
{previous_summary}

Now teach the content from the next page(s). Maintain continuity — do NOT re-introduce topics already covered. \
Use natural transitions like "Building on that…", "Now let's take this further…", "Next up…"
"""


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def _invoke_with_retry(chain, messages, max_retries: int = 5, initial_wait: float = 10.0) -> str:
    """Invoke chain with exponential backoff on 429 rate-limit errors."""
    wait = initial_wait
    for attempt in range(1, max_retries + 1):
        try:
            return await chain.ainvoke(messages)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                if attempt == max_retries:
                    raise
                print(f"[NotesNarrationChain] Rate limited (attempt {attempt}/{max_retries}). Waiting {wait:.0f}s...")
                await asyncio.sleep(wait)
                wait *= 2
            else:
                raise
    return ""


async def generate_notes_script(image_paths: List[str]) -> str:
    VISION_MODEL = os.getenv("MISTRAL_VISION_MODEL", "pixtral-12b-2409")
    llm = ChatMistralAI(model=VISION_MODEL, temperature=0.5, max_retries=2)
    parser = StrOutputParser()
    chain = llm | parser

    CHUNK_SIZE = 1
    full_script: List[str] = []
    total_pages = len(image_paths)
    previous_summary = ""

    for i in range(0, len(image_paths), CHUNK_SIZE):
        chunk_paths = image_paths[i:i + CHUNK_SIZE]

        # Build the message content
        content: List[Dict[str, Any]] = [{"type": "text", "text": _SYSTEM_PROMPT}]

        # Add continuity context after the first chunk
        if previous_summary:
            continuation = _CONTINUATION_PROMPT.format(previous_summary=previous_summary)
            content.append({"type": "text", "text": continuation})

        for idx, path in enumerate(chunk_paths):
            b64 = _encode_image(path)
            page_num = i + idx + 1
            content.append({"type": "text", "text": f"Teach the content from page {page_num} of {total_pages}."})
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })

        content.append({"type": "text", "text": "Generate the teaching narration now. Speak as if you're in a live class."})

        message = HumanMessage(content=content)
        chunk_num = i // CHUNK_SIZE + 1

        print(f"[NotesNarrationChain] Teaching page {chunk_num}/{total_pages} via {VISION_MODEL}...")
        chunk_script = await _invoke_with_retry(chain, [message])
        full_script.append(chunk_script)

        # Build a brief summary for continuity in the next chunk
        # Take the last ~100 chars as a rough summary hint
        if chunk_script:
            summary_snippet = chunk_script.strip()[-200:]
            previous_summary = f"...{summary_snippet}"

    return "\n\n".join(full_script)
