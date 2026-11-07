"""Voice: speech in (Whisper) and speech out (Kokoro for English, MMS for Arabic).

On the GPU Space the models run locally on the GPU (fast, no network). Without a GPU,
speech-to-text falls back to Hugging Face Inference (Whisper), and speech output is skipped
(the reply is still shown as text). A transcript goes through exactly the same path as a
typed message, so every behaviour, rule and test of the text chat applies to voice too.

    transcribe(path)  -> Transcript(text, error)
    speech(text)      -> (sample_rate, int16 samples) or None
    speakable(text)   -> the reply as plain sentences worth saying out loud
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import subprocess
import threading
from dataclasses import dataclass

import numpy as np

from core import cache

log = logging.getLogger(__name__)

ASR_MODEL = os.getenv("ASR_MODEL") or "openai/whisper-large-v3-turbo"
ASR_FALLBACK = os.getenv("ASR_FALLBACK") or "openai/whisper-large-v3"
TTS_EN = "hexgrad/Kokoro-82M"
TTS_EN_VOICE = os.getenv("TTS_VOICE") or "af_heart"
TTS_AR = "facebook/mms-tts-ara"
RATE = 16000              # Whisper input
OUT_RATE = 24000          # all speech output is resampled to this, so streamed chunks match
MAX_SECONDS = 60          # longer recordings are cut, so the wait stays short
MIN_SECONDS = 0.4
SILENCE_RMS = 0.004       # below this the recording is treated as silence (Whisper invents words in silence)
AUDIO_TYPES = (".wav", ".webm", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".opus")

# Phrases Whisper is known to produce from silence or noise.
HALLUCINATIONS = ("thank you for watching", "thanks for watching", "subscribe", "you", "thank you.", "bye.",
                  "اشتركوا في القناة", "شكرا لكم على المشاهدة", "ترجمة نانسي قنقر")

NOTHING_HEARD = "I didn't catch anything there. Try again, a bit closer to the mic, or type it."
ASR_DOWN = "I couldn't transcribe that right now. Please try again in a moment, or type your message."


@dataclass
class Transcript:
    text: str = ""
    error: str = ""


def is_audio(path: str) -> bool:
    return str(path).lower().endswith(AUDIO_TYPES)


# ---------------- device and local models ----------------

def _local_enabled() -> bool:
    """Run models locally when a GPU is present (or VOICE_LOCAL=1 forces it, e.g. on a Mac for testing)."""
    flag = os.getenv("VOICE_LOCAL", "auto").lower()
    if flag in ("0", "false", "no"):
        return False
    try:
        import torch
    except ImportError:
        return False
    return flag in ("1", "true", "yes") or torch.cuda.is_available()


def _device() -> str:
    import torch
    if torch.cuda.is_available():
        return "cuda"
    return "mps" if torch.backends.mps.is_available() else "cpu"


_models: dict = {}
_lock = threading.Lock()


def _asr():
    with _lock:
        if "asr" not in _models:
            import torch
            from transformers import pipeline
            dev = _device()
            _models["asr"] = pipeline("automatic-speech-recognition", model=ASR_MODEL, device=dev,
                                      torch_dtype=torch.float16 if dev != "cpu" else torch.float32)
        return _models["asr"]


def _kokoro():
    with _lock:
        if "kokoro" not in _models:
            from kokoro import KPipeline
            _models["kokoro"] = KPipeline(lang_code="a", repo_id=TTS_EN, device=_device() if _device() == "cuda" else None)
        return _models["kokoro"]


def _mms():
    with _lock:
        if "mms" not in _models:
            from transformers import AutoTokenizer, VitsModel
            dev = _device()
            _models["mms"] = (AutoTokenizer.from_pretrained(TTS_AR), VitsModel.from_pretrained(TTS_AR).to(dev), dev)
        return _models["mms"]


def warm() -> None:
    """Load the voice models in the background at startup, so the first voice message isn't slow."""
    if not _local_enabled():
        return
    for name, load in (("speech-to-text", _asr), ("English voice", _kokoro), ("Arabic voice", _mms)):
        try:
            load()
            log.info("Voice model ready: %s", name)
        except Exception as exc:
            log.warning("Could not load %s: %s", name, exc)


# ---------------- speech in ----------------

def _decode(path: str) -> np.ndarray:
    """Any audio file -> 16 kHz mono float32, via ffmpeg (handles wav, webm, mp3, m4a...)."""
    out = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path), "-t", str(MAX_SECONDS),
                          "-ac", "1", "-ar", str(RATE), "-f", "f32le", "-"], capture_output=True, timeout=30)
    if out.returncode != 0:
        raise ValueError(out.stderr.decode(errors="ignore")[:200])
    return np.frombuffer(out.stdout, dtype=np.float32)


def _wav_bytes(samples: np.ndarray, rate: int) -> bytes:
    import io
    import soundfile as sf
    buf = io.BytesIO()
    sf.write(buf, samples, rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return "" if text.lower().strip(" .!") in {h.strip(" .!") for h in HALLUCINATIONS} else text


def transcribe(path: str) -> Transcript:
    """Speech to text. Never raises: problems come back as a friendly error to show."""
    try:
        audio = _decode(path)
    except Exception as exc:
        log.warning("Could not decode audio %s: %s", path, exc)
        return Transcript(error="I couldn't read that recording. Please try again, or type your message.")
    if len(audio) < MIN_SECONDS * RATE or float(np.sqrt(np.mean(audio ** 2))) < SILENCE_RMS:
        return Transcript(error=NOTHING_HEARD)
    key = {"audio": hashlib.sha256(audio.tobytes()).hexdigest(), "model": ASR_MODEL}
    hit = cache.get("asr", key)
    if hit is not None:
        return Transcript(text=hit)
    text = None
    if _local_enabled():
        try:
            text = _asr()({"raw": audio, "sampling_rate": RATE})["text"]
        except Exception as exc:
            log.warning("Local speech-to-text failed, using Hugging Face Inference: %s", exc)
    if text is None:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=os.getenv("HF_TOKEN"), timeout=30)
        wav = _wav_bytes(audio, RATE)
        for model in (ASR_MODEL, ASR_FALLBACK):
            try:
                text = client.automatic_speech_recognition(wav, model=model).text
                break
            except Exception as exc:
                log.warning("Speech-to-text failed model=%s: %s", model, exc)
    if text is None:
        return Transcript(error=ASR_DOWN)
    text = _clean(text)
    if not text:
        return Transcript(error=NOTHING_HEARD)
    cache.put("asr", key, text)
    return Transcript(text=text)


# ---------------- speech out ----------------

_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿‍️]")


def speakable(text: str, limit: int = 420) -> str:
    """The reply as plain sentences: no markdown, emojis, bullets or ids; cut at a sentence boundary."""
    t = re.sub(r"`[^`]*`", "", text or "")
    t = re.sub(r"[*_#>]+", "", t)
    t = _EMOJI.sub("", t)
    t = re.sub(r"^\s*[•\-–✓?→·]\s*", "", t, flags=re.M)
    t = re.sub(r"\s*\n+\s*", ". ", t)
    t = re.sub(r"\.\s*\.", ".", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) <= limit:
        return t
    cut = max(t.rfind(p, 0, limit) for p in (". ", "? ", "! ", "۔ ", "؟ "))
    return t[: cut + 1] if cut > 0 else t[:limit]


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?؟])\s+", text.strip())
    return [p for p in parts if re.search(r"\w", p)]


def _arabic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum("؀" <= c <= "ۿ" for c in letters) / len(letters) > 0.3


def _resample(x: np.ndarray, src: int, dst: int) -> np.ndarray:
    if src == dst or len(x) == 0:
        return x
    n = int(len(x) * dst / src)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def speech(text: str) -> tuple[int, np.ndarray] | None:
    """One sentence (or a short reply) to audio at OUT_RATE, int16. None if speech output isn't available."""
    text = speakable(text)
    if not text or not _local_enabled():
        return None
    key = {"text": text, "voice": TTS_EN_VOICE}
    hit = cache.get("tts", key)
    if hit is not None:
        return OUT_RATE, np.asarray(hit, dtype=np.int16)
    try:
        if _arabic(text):
            import torch
            tok, model, dev = _mms()
            inputs = tok(text, return_tensors="pt").to(dev)
            with torch.no_grad():
                wav = model(**inputs).waveform[0].float().cpu().numpy()
            audio = _resample(wav, model.config.sampling_rate, OUT_RATE)
        else:
            chunks = [a for _, _, a in _kokoro()(text, voice=TTS_EN_VOICE)]
            audio = np.concatenate([c.cpu().numpy() if hasattr(c, "cpu") else np.asarray(c) for c in chunks])
    except Exception as exc:
        log.warning("Speech output failed: %s", exc)
        return None
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    if len(pcm) < OUT_RATE * 30:   # don't cache very long audio
        cache.put("tts", key, pcm.tolist())
    return OUT_RATE, pcm


def say_matches(matches: list[dict]) -> str:
    """A short spoken version of the recommendations."""
    if not matches:
        return ""
    names = [m["name"] for m in matches]
    listed = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    top = matches[0]
    line = top.get("summary", [top.get("reason", "")])[0] if top.get("summary") else top.get("reason", "")
    return f"I found {len(names)} {'person' if len(names) == 1 else 'people'}: {listed}. {line}"
