"""Cross-encoder reranking with BAAI/bge-reranker-v2-m3 on Hugging Face Inference.

The reranker reads what the member wants and each candidate's profile together and scores
the fit 0-1. It judges fit better than embeddings, which compare the two texts separately.
If it is slow or down, callers fall back to the embedding order.
"""

from __future__ import annotations

import logging
import os

import httpx

log = logging.getLogger(__name__)

DEFAULT_MODEL = "BAAI/bge-reranker-v2-m3"
TIMEOUT = 8.0  # seconds; past this the embedding order is good enough


def scores(query: str, passages: list[str]) -> list[float] | None:
    """One 0-1 score per passage, or None if the reranker is unavailable."""
    if not passages:
        return []
    from core import cache
    key = {"query": query, "passages": passages, "model": os.getenv("RERANK_MODEL") or DEFAULT_MODEL}
    hit = cache.get("rerank", key)
    if hit is not None:
        return hit
    token = os.getenv("HF_TOKEN")
    model = os.getenv("RERANK_MODEL") or DEFAULT_MODEL
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    body = {"inputs": [{"text": query, "text_pair": p} for p in passages]}
    try:
        r = httpx.post(url, headers={"Authorization": f"Bearer {token}"}, json=body, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        rows = data[0] if data and isinstance(data[0], list) else data
        out = [float(x["score"]) for x in rows]
        if len(out) != len(passages):
            raise ValueError(f"expected {len(passages)} scores, got {len(out)}")
        cache.put("rerank", key, out)
        return out
    except Exception as exc:
        log.warning("Reranker unavailable, using embedding order: %s", exc)
        return None
