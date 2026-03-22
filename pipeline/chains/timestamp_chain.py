"""
TimestampChain — LangChain chain for selecting pedagogically important segments.

Uses ChatMistralAI (text model) + ChatPromptTemplate + JsonOutputParser.
Returns a structured list of {start, end, reason} segment objects.
"""
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

TEXT_MODEL: str = os.getenv("MISTRAL_TEXT_MODEL", "mistral-large-latest")
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

_SYSTEM_PROMPT = """\
You are an expert educational content analyser for a platform that helps visually impaired students.

Analyse the lecture transcript below and identify the most pedagogically important moments where:
- A key concept, theorem, or definition is introduced or explained
- Mathematical equations, formulas, or derivations are written on the board
- Diagrams, graphs, plots, or visual proofs are being discussed
- Important conclusions, summaries, or topic transitions occur
- The lecturer is solving an example problem step by step

Return ONLY a valid JSON array — no explanation, no markdown, no code fences.
Each element must have exactly these fields:
  "start"  : start time in seconds (integer)
  "end"    : end time in seconds (integer)
  "reason" : one-sentence explanation of why this moment is important

Select between 10 and 20 of the most important, non-overlapping segments.
"""

_HUMAN_PROMPT = "Lecture transcript (with timestamps):\n\n{transcript}"


def build_timestamp_chain():
    """
    Build and return the LangChain timestamp-selection chain.

    Chain: ChatPromptTemplate | ChatMistralAI | JsonOutputParser
    Use with: await chain.ainvoke({"transcript": formatted_transcript_text})
    """
    llm = ChatMistralAI(
        model=TEXT_MODEL,
        api_key=MISTRAL_API_KEY,
        temperature=0,          # deterministic output for JSON parsing
        max_retries=3,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_PROMPT),
            ("human", _HUMAN_PROMPT),
        ]
    )

    return prompt | llm | JsonOutputParser()
