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
| `DATA_DIR` | Variable | `./runtime_data` (use `/data` on the Space) |
