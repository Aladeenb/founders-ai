---
title: Handshake
emoji: 🤝
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 6.31.0
python_version: "3.11"
app_file: app.py
hf_oauth: true
hf_oauth_expiration_minutes: 480
pinned: true
---

# Handshake

Your AI agent meets everyone in the startup ecosystem for you and comes back with the few conversations worth having.

Built for the Qai x Hugging Face hackathon, Doha, November 2026. All seeded profiles are fictional.

## Run locally

```bash
uv venv -p 3.11 .venv && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env   # add your HF_TOKEN
.venv/bin/python app.py
```

Check which models return valid JSON quickly: `.venv/bin/python scripts/probe_models.py`

## Configuration

| Name | Kind | Default |
|---|---|---|
| `HF_TOKEN` | Secret | none (needs Inference Providers permission) |
| `MODEL_ID` | Variable | `deepseek-ai/DeepSeek-V3.2` |
| `MODEL_FALLBACK` | Variable | `Qwen/Qwen3-Next-80B-A3B-Instruct` |
| `EMBEDDING_MODEL` | Variable | `intfloat/multilingual-e5-large` |
| `DATA_DIR` | Variable | `./runtime_data` (set `/data` only after enabling persistent storage) |

## Deploy to a Hugging Face Space

```bash
.venv/bin/python scripts/deploy_space.py --dry-run   # check the token, list the files; changes nothing
.venv/bin/python scripts/deploy_space.py             # deploy to <token owner>/handshake
```

The script reads `HF_TOKEN` from `.env`, creates the Space if needed, stores the token as the Space's
`HF_TOKEN` secret, sets the model variables, uploads the working tree (never `.env`, `.venv` or
`runtime_data`), waits for the build and prints the link. Pass `--space owner/name` to deploy elsewhere.

- **Token:** a fine-grained token with *Make calls to Inference Providers* (the app needs it) and
  *Write access to contents/settings* for the namespace you deploy to. It is stored on the Space as a
  secret, so give it nothing else.
- **Namespace:** Gradio Spaces on free CPU are free under a personal account. An organization needs a
  Team or Enterprise plan to host one, so deploying to `foundersai/...` fails until it has one.
- **Storage:** `DATA_DIR` is left unset. On a free Space `/data` does not exist, so profiles saved by
  signed-in users live in `./runtime_data` and reset when the Space restarts. Seed profiles and the
  demo cache ship with the code, so the demo always works.
