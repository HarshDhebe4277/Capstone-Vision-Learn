"""
NarrationChain — Generates pedagogical narration scripts using text-only mode.

Uses mistral-large-latest (same as timestamp selection) with the full transcript
plus frame metadata (timestamps + reasons) as rich text context.

Why text-only?
- Avoids Pixtral/Vision API rate limits (429)
- The transcript + LLM-annotated frame reasons already capture all the
  educational content needed for a high-quality narration
- mistral-large-latest is faster and has more generous rate limits
"""
import os
from typing import Any, Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

TEXT_MODEL: str = os.getenv("MISTRAL_TEXT_MODEL", "mistral-large-latest")
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

_SYSTEM_PROMPT = """\
You are a first-person teacher creating a structured audio narration for blind and visually impaired students. \
The output will be read aloud by a text-to-speech engine, so it must be precise, dense, and well-structured.

═══ MANDATORY OUTPUT STRUCTURE ═══

Each major topic or transition must follow this pattern exactly:

  [Section Marker] e.g. "Concept:", "Example:", "Important Rule:", "Step 1:", "Step 2:", "Summary:"
  [1-3 sentences of explanation — clear, first-person, spoken language]
  [PAUSE]

Use [PAUSE] literally on its own line between each distinct section. \
This creates natural breakpoints for listeners.

═══ STRICT RULES — DO NOT BREAK ANY OF THESE ═══

1. NO FLUFF. Remove ALL of the following:
   - Greetings: "Welcome", "I'm glad you're here", "Hello everyone"
   - Encouragement: "You've got this", "Great question", "Happy learning"
   - Filler: "So", "Now then", "Alright", "Let's dive in"
   Begin directly with teaching content.

2. VISUAL REFERENCES — at every key moment listed, explicitly say what is on the screen:
   - Good: "On the board, I have written..."  "The diagram now shows..."
   - Good: "You can see on the slide that..."  "I am now drawing..."
   - Bad: "Let's apply this to our function."  (no visual reference)

3. MATH VERBALIZATION — always use the full sentence form:
   - Good: "The derivative of two x squared is four x."
   - Good: "f of x equals two x squared plus three x plus five"
   - Bad:  "two times two x, which is four x"  (ambiguous)
   - Bad:  "d/dx of x squared equals two x"   (reads like notation, not speech)
   Every symbol must be spoken: ∴ → "therefore", ∫₀^∞ → "the integral from zero to infinity of", → → "gives us" or "approaches"

4. STRUCTURE MARKERS — every major idea must be labelled:
   - Use: "Concept:", "Definition:", "Example:", "Step 1:", "Step 2:", "Important Rule:", "Caution:", "Summary:"
   - This is mandatory, not optional.

5. INFORMATION DENSITY — eliminate redundancy:
   - Say each idea once, correctly, clearly.
   - Do not repeat the same sentence in different words.

6. RECAP — end with a numbered list, maximum 8 items, NO explanations in the recap:
   Example format:
   "Summary: Today we covered four key rules.
   One: The Power Rule.
   Two: The Product Rule.
   Three: The Quotient Rule.
   Four: The Chain Rule.
   End of lecture."

7. USE THE VISUAL CONTEXT — for each key moment provided, reference what is visible at that timestamp. \
   Never narrate a key moment without describing what is on the board or slide.
"""

_HUMAN_TEMPLATE = """\
## Full Lecture Transcript (with timestamps)

{transcript}

---

## Key Visual Moments to Narrate

{frame_context}

---

Generate the complete audio narration script now. Plain spoken text only, no formatting:
"""


def _build_frame_context(frames: List[Dict[str, Any]]) -> str:
    """Convert frame metadata into a rich text description for the LLM."""
    lines = []
    for i, frame in enumerate(frames):
        ts = frame["timestamp"]
        mm, ss = int(ts) // 60, int(ts) % 60
        reason = frame.get("reason", "key visual moment")
        lines.append(f"[{mm:02d}:{ss:02d}] — {reason}")
    return "\n".join(lines)


async def generate_narration_script(
    frames: List[Dict[str, Any]],
    transcript: str,
) -> str:
    """
    Generate a pedagogical narration script using text-only Mistral Large.

    Sends the full transcript + frame timestamp/reason metadata as text.
    No images are sent — avoids Pixtral vision API rate limits entirely.
    """
    llm = ChatMistralAI(
        model=TEXT_MODEL,
        api_key=MISTRAL_API_KEY,
        temperature=0.4,
        max_retries=3,
    )

    frame_context = _build_frame_context(frames)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_TEMPLATE),
    ])

    chain = prompt | llm | StrOutputParser()

    print(f"[NarrationChain] Generating script with {TEXT_MODEL} "
          f"({len(frames)} key moments, text-only mode)...")

    return await chain.ainvoke({
        "transcript": transcript,
        "frame_context": frame_context,
    })
