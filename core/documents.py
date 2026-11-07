"""Read whatever a member uploads: CV, pitch deck, fund deck, thesis, one-pager.

PDF pages with real text are read directly. Pages that are mostly images (common in pitch
decks) are rendered and read by a vision model, so traction on a slide isn't missed.
Word and PowerPoint are read from their XML; images go straight to the vision model.
"""

from __future__ import annotations

import io
import logging
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.etree import ElementTree

from core import llm

log = logging.getLogger(__name__)

MAX_PAGES = 20            # pages read from one PDF
MAX_VISION_PAGES = 10     # image-only pages sent to the vision model (cost and waiting time)
MIN_PAGE_TEXT = 200       # fewer characters than this means the page is mostly an image
MAX_CHARS = 12000         # text kept from one upload
SUPPORTED = (".pdf", ".docx", ".pptx", ".txt", ".md", ".png", ".jpg", ".jpeg", ".webp")

VISION_PROMPT = ("Transcribe all text on this page or slide, including numbers in charts and tables, as plain "
                 "lines. If there is no text, describe in one line what the image shows.")


class DocumentError(ValueError):
    """Friendly message safe to show the member."""


def read(path: str | Path) -> str:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise DocumentError("Please upload a PDF, Word, PowerPoint, text or image file, or just tell me about yourself.")
    try:
        if suffix == ".pdf":
            text = _pdf(path)
        elif suffix == ".docx":
            text = _xml_text(path, ["word/document.xml"], "w")
        elif suffix == ".pptx":
            text = _pptx(path)
        elif suffix in (".txt", ".md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
        else:
            text = _image(path.read_bytes())
    except DocumentError:
        raise
    except Exception as exc:
        log.warning("Could not read %s: %s", path.name, exc)
        raise DocumentError("I couldn't read that file. Could you tell me about yourself here instead?") from exc
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 40:
        raise DocumentError("That file looks empty. Could you tell me about yourself here instead?")
    return text[:MAX_CHARS]


# ---------------- formats ----------------

def _pdf(path: Path) -> str:
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(path))
    n = min(len(pdf), MAX_PAGES)
    texts = [pdf[i].get_textpage().get_text_range() for i in range(n)]
    image_pages = [i for i, t in enumerate(texts) if len(t.strip()) < MIN_PAGE_TEXT][:MAX_VISION_PAGES]
    if image_pages:
        pngs = {i: _render(pdf[i]) for i in image_pages}
        with ThreadPoolExecutor(max_workers=5) as pool:
            for i, text in zip(image_pages, pool.map(lambda i: _vision_or_blank(pngs[i]), image_pages)):
                if len(text.strip()) > len(texts[i].strip()):
                    texts[i] = text
    joined = "\n\n".join(f"[Page {i + 1}]\n{t.strip()}" for i, t in enumerate(texts) if t.strip())
    if image_pages and len(joined) < 40:
        raise DocumentError("That file is mostly images and I couldn't read them right now. Could you type the key "
                            "points (what you do, stage, traction, what you need), or try again in a minute?")
    return joined


def _render(page) -> bytes:
    image = page.render(scale=1.5).to_pil()
    image.thumbnail((1600, 1600))
    buf = io.BytesIO()
    image.save(buf, "PNG")
    return buf.getvalue()


def _vision_or_blank(png: bytes) -> str:
    try:
        return llm.read_image(png, VISION_PROMPT)
    except llm.LLMError:
        return ""


def _image(data: bytes) -> str:
    from PIL import Image
    image = Image.open(io.BytesIO(data)).convert("RGB")
    image.thumbnail((1600, 1600))
    buf = io.BytesIO()
    image.save(buf, "PNG")
    try:
        return llm.read_image(buf.getvalue(), VISION_PROMPT)
    except llm.LLMError as exc:
        raise DocumentError("I couldn't read that image right now. Could you type the key points instead?") from exc


_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
       "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def _xml_text(path: Path, parts: list[str], prefix: str) -> str:
    """Paragraph text from Office XML parts (w:p/w:t for Word, a:p/a:t for slides)."""
    ns = "{" + _NS[prefix] + "}"
    out = []
    with zipfile.ZipFile(path) as z:
        for part in parts:
            root = ElementTree.fromstring(z.read(part))
            out += ["".join(t.text or "" for t in p.iter(ns + "t")) for p in root.iter(ns + "p")]
    return "\n".join(line for line in out if line.strip())


def _pptx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        slides = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                        key=lambda n: int(re.search(r"\d+", n).group()))[:MAX_PAGES]
    texts = [_xml_text(path, [s], "a") for s in slides]
    return "\n\n".join(f"[Slide {i + 1}]\n{t}" for i, t in enumerate(texts) if t.strip())
