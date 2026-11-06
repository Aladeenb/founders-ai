"""Compare candidate models on speed and valid JSON. Run before choosing MODEL_ID.

Usage: python scripts/probe_models.py [model ...]
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pydantic import BaseModel

from core import llm

CANDIDATES = [
    "meta-llama/Llama-3.3-70B-Instruct",
    "Qwen/Qwen3-Next-80B-A3B-Instruct",
    "Qwen/Qwen3-235B-A22B-Instruct-2507",
    "openai/gpt-oss-120b",
    "deepseek-ai/DeepSeek-V3.2",
]

PROMPT = [
    {"role": "system", "content": "Reply with only a JSON object with keys: message (string, under 40 words), stage (one of opening, exploring, negotiating, verdict), wants_to_end (boolean)."},
    {"role": "user", "content": "You are a founder's agent opening a conversation with an investor's agent about a Seed round for a Doha fintech."},
]


class Probe(BaseModel):
    message: str
    stage: str
    wants_to_end: bool


def main() -> None:
    load_dotenv()
    client = llm._client()
    for model in sys.argv[1:] or CANDIDATES:
        ok, times = 0, []
        for _ in range(3):
            start = time.time()
            try:
                text = llm._complete(client, model, PROMPT, 200, json_mode=True)
                Probe.model_validate(llm.extract_json(text))
                ok += 1
            except Exception as exc:
                print(f"  {model}: {type(exc).__name__}: {str(exc)[:120]}")
            times.append(time.time() - start)
        print(f"{model:45s} valid {ok}/3   avg {sum(times) / len(times):.1f}s")


if __name__ == "__main__":
    main()
