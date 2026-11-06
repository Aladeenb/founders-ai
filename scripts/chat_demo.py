"""Test page for the AI layer (core/intake.py + core/matchmaker.py). Not the real frontend.

Run:  .venv/bin/python scripts/chat_demo.py   ->  http://127.0.0.1:7870
      AI_CACHE_DIR=./ai_cache .venv/bin/python scripts/chat_demo.py   (rehearsals replay instantly)

Shows the frontend how to wire it: intake.start() on load, intake.send() per message (with an
optional upload), then matchmaker.find() once the profile is confirmed, matchmaker.chat() for
follow-ups and matchmaker.draft_intro() for the intro.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from core import intake, matchmaker  # noqa: E402

STEP_TEXT = {
    "scan": lambda d: f"🔎 Looking through {d['total']} people…",
    "filter": lambda d: f"✓ {d['label']}: {d['kept']} left",
    "narrow": lambda d: f"✓ Narrowed {d['considered']} to the closest {d['kept']}",
    "rerank": lambda d: f"✓ Scored {d['scored']} on fit, kept the top {d['kept']}",
    "fit": lambda d: f"· {d['name']}: {d['level']}",
}


def cards(matches: list[dict]) -> str:
    if not matches:
        return "_No recommendations yet._"
    icons = ("✓", "?", "→")
    return "\n\n".join(f"**{m['name']}** · {m['role']} · {m['score']} ({m['fit']})  \n{m['headline']}  \n" +
                         "  \n".join(f"{icons[i] if i < 3 else '·'} {line}" for i, line in enumerate(m["summary"])) +
                         f"  \n`{m['id']}`" for m in matches)


def begin():
    st = intake.start()
    return st["session_id"], "intake", [{"role": "assistant", "content": st["reply"]}], {}, cards([])


def _stream_search(gen, history):
    """Show search steps live in one bubble, then any reply. Yields (history, matches or None)."""
    lines, bubble, matches = [], None, None
    for kind, data in gen:
        if kind in STEP_TEXT:
            lines.append(STEP_TEXT[kind](data))
            if bubble is None:
                history = history + [{"role": "assistant", "content": ""}]
                bubble = len(history) - 1
            history[bubble]["content"] = "\n".join(lines)
            yield history, None
        elif kind == "done":
            matches = matchmaker.as_dicts(data["matches"])
            if data.get("message"):
                history = history + [{"role": "assistant", "content": data["message"]}]
        elif kind == "reply":
            matches = data["matches"]
            history = history + [{"role": "assistant", "content": data["text"]}]
    yield history, matches


def chat(message: dict, history: list, sid: str, mode: str):
    text, files = message.get("text", ""), message.get("files", [])
    history = history + [{"role": "user", "content": text or ("📎 " + Path(files[0]).name if files else "")}]
    if mode == "intake":
        st = intake.send(sid, text, file=files[0] if files else None)
        history = history + [{"role": "assistant", "content": st["reply"]}]
        prof = {**st["profile"], "_missing": st["missing"], "_done": st["done"]}
        yield history, None, prof, gr.skip(), mode
        if not st["done"]:
            return
        mode = "match"
        for history, matches in _stream_search(matchmaker.find(sid), history):
            yield history, None, prof, cards(matches) if matches is not None else gr.skip(), mode
        if matches:
            history = history + [{"role": "assistant", "content": "Ask me to refine the list, why someone isn't on "
                                                                  "it, for more people like someone, or what to ask them."}]
            yield history, None, prof, gr.skip(), mode
        return
    for history, matches in _stream_search(matchmaker.chat(sid, text), history):
        yield history, None, gr.skip(), cards(matches) if matches is not None else gr.skip(), mode


def intro(person_id: str, sid: str, history: list):
    try:
        text = matchmaker.draft_intro(sid, person_id.strip())
    except (ValueError, KeyError) as exc:
        text = str(exc)
    return history + [{"role": "assistant", "content": "✉️ Intro draft:\n\n" + text}]


with gr.Blocks(title="Handshake AI layer test") as demo:
    sid, mode = gr.State(""), gr.State("intake")
    with gr.Row():
        with gr.Column(scale=3):
            bot = gr.Chatbot(height=560, label="Handshake agent")
            box = gr.MultimodalTextbox(file_types=[".pdf", ".docx", ".pptx", ".txt", ".png", ".jpg"],
                                       placeholder="Type, or attach a CV / pitch deck / fund deck", show_label=False)
        with gr.Column(scale=2):
            found = gr.Markdown(label="Recommendations")
            with gr.Row():
                pid = gr.Textbox(placeholder="person id, e.g. i-ali", show_label=False, scale=3)
                gr.Button("Draft intro", scale=1).click(intro, [pid, sid, bot], bot)
            with gr.Accordion("Profile (live)", open=False):
                prof = gr.JSON()
            gr.Button("Restart").click(begin, outputs=[sid, mode, bot, prof, found])
    demo.load(begin, outputs=[sid, mode, bot, prof, found])
    box.submit(chat, [box, bot, sid, mode], [bot, box, prof, found, mode])

if __name__ == "__main__":
    import os
    on_space = bool(os.getenv("SPACE_ID"))
    demo.launch(server_name="0.0.0.0" if on_space else None, server_port=7860 if on_space else 7870)
