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

from core import intake, matchmaker, voice  # noqa: E402

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


def _speak(text: str, on: bool):
    """Audio for one sentence or a short reply, or gr.skip() when voice is off or unavailable."""
    if not on or not text:
        return gr.skip()
    out = voice.speech(text)
    return out if out is not None else gr.skip()


def chat(message: dict, history: list, sid: str, mode: str, speak: bool):
    """Outputs: chat, input box, profile, recommendations, mode, voice audio."""
    text, files = message.get("text", ""), list(message.get("files", []))
    skip = gr.skip()
    audio_in = next((f for f in files if voice.is_audio(f)), None)
    if audio_in:                                   # voice message: transcribe, then treat exactly like typed text
        files.remove(audio_in)
        history = history + [{"role": "user", "content": "🎤 …"}]
        yield history, None, skip, skip, mode, skip
        heard = voice.transcribe(audio_in)
        if heard.error:
            history[-1]["content"] = "🎤 (nothing heard)"
            history = history + [{"role": "assistant", "content": heard.error}]
            yield history, None, skip, skip, mode, _speak(heard.error, speak)
            return
        text = (text + " " + heard.text).strip()
        history[-1]["content"] = "🎤 " + heard.text
    else:
        history = history + [{"role": "user", "content": text or ("📎 " + Path(files[0]).name if files else "")}]
    doc = files[0] if files else None

    if mode == "intake":
        history = history + [{"role": "assistant", "content": ""}]
        st, said = None, []
        for kind, data in intake.send_stream(sid, text, file=doc):
            if kind == "say":
                said.append(data)
                history[-1]["content"] = " ".join(said)
                yield history, None, skip, skip, mode, _speak(data, speak)
            else:
                st = data
        history[-1]["content"] = st["reply"]
        prof = {**st["profile"], "_missing": st["missing"], "_done": st["done"]}
        yield history, None, prof, skip, mode, skip
        if not st["done"]:
            return
        mode = "match"
        matches = None
        for history, matches in _stream_search(matchmaker.find(sid), history):
            yield history, None, prof, cards(matches) if matches is not None else skip, mode, skip
        spoken = voice.say_matches(matches or []) or (history[-1]["content"] if not matches else "")
        if matches:
            history = history + [{"role": "assistant", "content": "Ask me to refine the list, why someone isn't on "
                                                                  "it, for more people like someone, or what to ask them."}]
        yield history, None, prof, skip, mode, _speak(spoken, speak)
        return
    reply = ""
    for history, matches in _stream_search(matchmaker.chat(sid, text), history):
        if matches is not None:
            reply = history[-1]["content"]
        yield history, None, skip, cards(matches) if matches is not None else skip, mode, skip
    for sentence in voice.sentences(voice.speakable(reply)):
        yield history, None, skip, skip, mode, _speak(sentence, speak)


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
            box = gr.MultimodalTextbox(file_types=[".pdf", ".docx", ".pptx", ".txt", ".png", ".jpg", *voice.AUDIO_TYPES],
                                       sources=["upload", "microphone"], show_label=False,
                                       placeholder="Type, talk (🎤), or attach a CV / pitch deck / fund deck")
            with gr.Row():
                speak = gr.Checkbox(value=True, label="🔊 Speak replies", scale=1)
                player = gr.Audio(streaming=True, autoplay=True, show_label=False, interactive=False, scale=3)
        with gr.Column(scale=2):
            found = gr.Markdown(label="Recommendations")
            with gr.Row():
                pid = gr.Textbox(placeholder="person id, e.g. i-ali", show_label=False, scale=3)
                gr.Button("Draft intro", scale=1).click(intro, [pid, sid, bot], bot)
            with gr.Accordion("Profile (live)", open=False):
                prof = gr.JSON()
            gr.Button("Restart").click(begin, outputs=[sid, mode, bot, prof, found])
    demo.load(begin, outputs=[sid, mode, bot, prof, found])
    box.submit(chat, [box, bot, sid, mode, speak], [bot, box, prof, found, mode, player])

if __name__ == "__main__":
    import os
    import threading
    threading.Thread(target=voice.warm, daemon=True).start()   # load voice models on the GPU in the background
    on_space = bool(os.getenv("SPACE_ID"))
    demo.launch(server_name="0.0.0.0" if on_space else None, server_port=7860 if on_space else 7870)
