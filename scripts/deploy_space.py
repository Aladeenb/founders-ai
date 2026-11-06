"""Deploy the current working tree to a Hugging Face Space.

Usage:
    python scripts/deploy_space.py --dry-run        # check token and list files, change nothing
    python scripts/deploy_space.py                  # create/update <token owner>/handshake
    python scripts/deploy_space.py --space foundersai/handshake

The default is the token owner's personal namespace: Gradio Spaces on free CPU are free for
users, but an organization needs a Team or Enterprise plan to host one.

Reads HF_TOKEN from .env. The same token is stored on the Space as the HF_TOKEN secret, so it
needs both Inference Providers access (for the app) and write access to the target namespace
(for this script).

DATA_DIR is not set: on a free Space /data does not exist, so the app keeps its default
./runtime_data, which resets when the Space restarts. Set DATA_DIR=/data only after enabling
persistent storage.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from dotenv import dotenv_values
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError, filter_repo_objects

ROOT = Path(__file__).resolve().parent.parent
SPACE_NAME = "handshake"
VARIABLES = ("MODEL_ID", "MODEL_FALLBACK", "EMBEDDING_MODEL")
IGNORE = [".env", ".env.*", ".venv/*", ".git/*", "runtime_data/*", ".gradio/*", ".pytest_cache/*",
          "**/__pycache__/*", "*.pyc", "screenshots/*", ".DS_Store", "**/.DS_Store"]


def check_token(api: HfApi, namespace: str) -> list[str]:
    """Return a list of problems with the token for this deploy (empty means fine)."""
    info = api.whoami()
    access = info["auth"]["accessToken"]
    if access["role"] == "write":
        return []
    if access["role"] == "read":
        return ["The token is read-only. It needs write access to " + namespace + "."]
    scoped = (access.get("fineGrained") or {}).get("scoped", [])
    perms = {s["entity"]["name"]: set(s["permissions"]) for s in scoped}
    problems = []
    if "repo.write" not in perms.get(namespace, set()):
        problems.append(f'The token has no "Write access to contents/settings of all repos" for {namespace}.')
    if not any("inference.serverless.write" in p for p in perms.values()):
        problems.append('The token has no "Make calls to Inference Providers" permission; the app\'s AI calls would fail.')
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--space", help="owner/name (default: <token owner>/handshake)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = dotenv_values(ROOT / ".env")
    token = env.get("HF_TOKEN") or ""
    if not token.startswith("hf_") or "your_token" in token:
        print("No HF_TOKEN in .env.")
        return 1
    api = HfApi(token=token)
    args.space = args.space or f"{api.whoami()['name']}/{SPACE_NAME}"
    namespace = args.space.split("/")[0]

    problems = check_token(api, namespace)
    for p in problems:  # warnings only: the create call below is the real test
        print("Token warning:", p)

    # Same filter upload_folder applies, so the dry run lists exactly what would be uploaded.
    files = sorted(filter_repo_objects((p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()),
                                       ignore_patterns=IGNORE))
    if args.dry_run:
        print(f"Would deploy {len(files)} files to https://huggingface.co/spaces/{args.space}:")
        for f in files:
            print("  ", f)
        print("Variables:", {k: env.get(k) for k in VARIABLES if env.get(k)})
        print("Secret: HF_TOKEN (from .env)")
        return 0

    try:
        api.create_repo(args.space, repo_type="space", space_sdk="gradio", exist_ok=True)
    except HfHubHTTPError as exc:
        print("Could not create the Space:", str(exc).splitlines()[-1])
        return 1
    api.add_space_secret(args.space, "HF_TOKEN", token)
    for key in VARIABLES:
        if env.get(key):
            api.add_space_variable(args.space, key, env[key])
    commit = api.upload_folder(repo_id=args.space, repo_type="space", folder_path=ROOT,
                               ignore_patterns=IGNORE, commit_message="Deploy from local working tree")
    print("Uploaded:", commit.commit_url)

    print("Building", end="", flush=True)
    for _ in range(90):  # up to 15 minutes
        stage = api.get_space_runtime(args.space).stage
        if stage in ("RUNNING", "BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"):
            break
        print(".", end="", flush=True)
        time.sleep(10)
    print(f"\nStage: {stage}")
    print(f"Space: https://huggingface.co/spaces/{args.space}")
    return 0 if stage == "RUNNING" else 1


if __name__ == "__main__":
    sys.exit(main())
