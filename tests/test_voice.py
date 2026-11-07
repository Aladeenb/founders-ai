"""Voice: transcription safeguards, fallbacks, speakable text, and streaming that matches the text path."""

import numpy as np
import pytest
import soundfile as sf

from core import intake, llm, voice


def wav(path, seconds=2.0, loud=True, rate=16000):
    t = np.linspace(0, seconds, int(rate * seconds), endpoint=False)
    sig = (0.2 * np.sin(2 * np.pi * 220 * t)) if loud else np.zeros_like(t)
    sf.write(path, sig.astype(np.float32), rate)
    return str(path)


@pytest.fixture
def no_local(monkeypatch):
    monkeypatch.setenv("VOICE_LOCAL", "0")


def test_silence_and_too_short_are_caught_without_any_model_call(tmp_path, no_local, monkeypatch):
    monkeypatch.setattr("huggingface_hub.InferenceClient", lambda **k: pytest.fail("no model call for silence"))
    assert voice.transcribe(wav(tmp_path / "s.wav", loud=False)).error == voice.NOTHING_HEARD
    assert voice.transcribe(wav(tmp_path / "short.wav", seconds=0.2)).error == voice.NOTHING_HEARD


def test_unreadable_audio_is_friendly(tmp_path, no_local):
    bad = tmp_path / "x.webm"
    bad.write_bytes(b"not audio")
    assert "couldn't read that recording" in voice.transcribe(str(bad)).error


class FakeClient:
    calls = []

    def __init__(self, fail=(), text="Hi, I'm Maha."):
        self.fail, self.text = fail, text

    def automatic_speech_recognition(self, audio, model):
        FakeClient.calls.append(model)
        if model in self.fail:
            raise RuntimeError("down")
        return type("R", (), {"text": self.text})()


def test_api_fallback_when_no_gpu(tmp_path, no_local, monkeypatch):
    FakeClient.calls = []
    monkeypatch.setattr("huggingface_hub.InferenceClient", lambda **k: FakeClient(fail=(voice.ASR_MODEL,)))
    out = voice.transcribe(wav(tmp_path / "a.wav"))
    assert out.text == "Hi, I'm Maha." and FakeClient.calls == [voice.ASR_MODEL, voice.ASR_FALLBACK]


def test_all_speech_models_down(tmp_path, no_local, monkeypatch):
    monkeypatch.setattr("huggingface_hub.InferenceClient",
                        lambda **k: FakeClient(fail=(voice.ASR_MODEL, voice.ASR_FALLBACK)))
    assert voice.transcribe(wav(tmp_path / "a.wav")).error == voice.ASR_DOWN


def test_whisper_hallucinations_are_dropped(tmp_path, no_local, monkeypatch):
    monkeypatch.setattr("huggingface_hub.InferenceClient", lambda **k: FakeClient(text=" Thank you for watching! "))
    assert voice.transcribe(wav(tmp_path / "a.wav")).error == voice.NOTHING_HEARD


def test_speakable_strips_markup_and_ids():
    text = "**Nadia Karim** · investor\n✓ Leads seed rounds 🎉\n? Nothing obvious\n→ Ask about banks\n`i-nadia`"
    out = voice.speakable(text)
    assert "**" not in out and "i-nadia" not in out and "🎉" not in out and "✓" not in out
    assert "Leads seed rounds" in out and "Ask about banks" in out


def test_speech_is_skipped_without_gpu(no_local):
    assert voice.speech("Hello there.") is None          # the reply is still shown as text


def test_say_matches():
    ms = [{"name": "Nadia Karim", "summary": ["Leads seed fintech rounds."]}, {"name": "Ravi Menon", "summary": []}]
    assert voice.say_matches(ms) == "I found 2 people: Nadia Karim and Ravi Menon. Leads seed fintech rounds."
    assert voice.say_matches([]) == ""


# ---------- streaming ----------

def test_partial_reply_is_read_while_streaming():
    assert llm._partial_string('{"reply": "Hi Maha. What\\u2019s', "reply") == ("Hi Maha. What’s", False)
    assert llm._partial_string('{"reply": "Done.", "role": null}', "reply") == ("Done.", True)


def test_send_stream_matches_send(monkeypatch):
    """Voice uses the same turn logic as text: same state, plus the reply as spoken sentences."""
    turn = {"reply": "Hi Maha. What are you raising?", "role": "founder", "profile": {"display_name": "Maha"}}

    def fake_stream(messages, schema, **k):
        yield ("sentence", "Hi Maha.")
        yield ("sentence", "What are you raising?")
        yield ("result", (schema.model_validate(turn), "fake"))

    monkeypatch.setattr(llm, "stream_json", fake_stream)
    monkeypatch.setattr(llm, "chat_json", lambda m, schema, **k: (schema.model_validate(turn), "fake"))
    a = intake.send(intake.start()["session_id"], "I'm Maha")
    events = list(intake.send_stream(intake.start()["session_id"], "I'm Maha"))
    said = [d for k, d in events if k == "say"]
    state = events[-1][1]
    assert said == ["Hi Maha.", "What are you raising?"]
    assert state["reply"] == a["reply"] and state["profile"] == a["profile"]


def test_stream_failure_falls_back_to_normal_call(monkeypatch):
    class Boom:
        class chat:
            class completions:
                @staticmethod
                def create(**k):
                    raise RuntimeError("stream broke")

    monkeypatch.setattr(llm, "_client", lambda timeout=0: Boom())
    monkeypatch.setattr(llm, "chat_json", lambda m, schema, **k: (schema(questions=["a"]), "fallback"))
    from core.matchmaker import _Questions
    events = list(llm.stream_json([{"role": "user", "content": "x"}], _Questions))
    assert events == [("result", (_Questions(questions=["a"]), "fallback"))]
