"""Precompute E5 embeddings for the seed profiles.

Run after editing data/seed_profiles.json:
    .venv/bin/python scripts/seed.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv()

from core import matching, storage  # noqa: E402


def main() -> None:
    profiles = storage.seed_profiles()
    queries = matching.embed([matching.query_text(p) for p in profiles])
    passages = matching.embed([matching.passage_text(p) for p in profiles])
    np.savez_compressed(
        matching.EMBED_FILE,
        ids=np.array([p.id for p in profiles]),
        query=queries.astype(np.float32),
        passage=passages.astype(np.float32),
    )
    print(f"Saved {len(profiles)} profiles x {queries.shape[1]} dims to {matching.EMBED_FILE}")

    matching._seed_vectors.cache_clear()
    for pid in ("f-layla", "i-omar", "t-sara"):
        viewer = storage.get_profile(pid)
        ranked = matching.rank(viewer, k=5)
        print(f"\n{viewer.display_name}:")
        for p, s in ranked:
            print(f"  {s:3d}  {p.display_name:22s} {p.headline[:60]}")


if __name__ == "__main__":
    main()
