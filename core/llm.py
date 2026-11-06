"""LLM calls through Hugging Face Inference Providers (OpenAI-compatible router).

Every call has a 20-second timeout. A failed call or invalid JSON is retried once
on the primary model, then the fallback model is tried.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

log = logging.getLogger(__name__)

ROUTER_URL = "https://router.huggingface.co/v1"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3.2"
DEFAULT_FALLBACK = "Qwen/Qwen3-Next-80B-A3B-Instruct"
TIMEOUT_SECONDS = 20
DEFAULT_MAX_TOKENS = 400

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Raised when every model attempt fails. The message is safe to show users."""


def models() -> list[str]:
    primary = os.getenv("MODEL_ID") or DEFAULT_MODEL
    fallback = os.getenv("MODEL_FALLBACK") or DEFAULT_FALLBACK
    return [primary] if fallback == primary else [primary, fallback]


def _client() -> OpenAI:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise LLMError("The AI service is not configured yet (missing HF_TOKEN).")
    return OpenAI(base_url=ROUTER_URL, api_key=token, timeout=TIMEOUT_SECONDS, max_retries=0)


def _complete(client: OpenAI, model: str, messages: list[dict], max_tokens: int, json_mode: bool) -> str:
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    resp = client.chat.completions.create(
        model=model, messages=messages, max_tokens=max_tokens, temperature=0.4, **kwargs
    )
    return (resp.choices[0].message.content or "").strip()


def chat(messages: list[dict], max_tokens: int = DEFAULT_MAX_TOKENS) -> tuple[str, str]:
    """Return (text, model_used)."""
    client = _client()
    for model in models():
        for attempt in range(2):
            try:
                text = _complete(client, model, messages, max_tokens, json_mode=False)
                if text:
                    return text, model
            except Exception as exc:  # network, timeout, provider errors
                log.warning("LLM call failed model=%s attempt=%d: %s", model, attempt, exc)
                break  # API errors go straight to the fallback model
    raise LLMError("The AI service is busy right now. Please try again in a moment.")


def extract_json(text: str) -> dict:
    """Parse a JSON object from model output, tolerating code fences and stray prose."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def chat_json(messages: list[dict], schema: type[T], max_tokens: int = DEFAULT_MAX_TOKENS) -> tuple[T, str]:
    """Return (validated model instance, model_used)."""
    client = _client()
    for model in models():
        for attempt in range(2):
            try:
                text = _complete(client, model, messages, max_tokens, json_mode=True)
                return schema.model_validate(extract_json(text)), model
            except (json.JSONDecodeError, ValidationError) as exc:
                log.warning("Invalid JSON model=%s attempt=%d: %s", model, attempt, exc)
            except Exception as exc:
                log.warning("LLM call failed model=%s attempt=%d: %s", model, attempt, exc)
                break
    raise LLMError("The AI service gave an unexpected answer. Please try again.")
