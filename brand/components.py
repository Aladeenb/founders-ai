"""Markup for the brand components, rendered with gr.HTML.

Every value that comes from a founder or a model is escaped with html.escape before it enters HTML.
Founder text reaches the other founder's screen, so unescaped text would let one founder run script
in the other's browser. Agents are shown by name only: there are no agent marks or avatars.
"""
from html import escape as e

STATE_LABELS = {"listening": "Listening", "thinking": "Thinking", "speaking": "Speaking",
                "matching": "Matching", "ready": "Ready"}

TOPICS = ["idea", "roles", "commitment", "runway", "location", "CEO", "dealbreakers", "risk",
          "working style", "values", "equity"]


def wordmark():
    return '<span class="fw-wordmark">Fahem &amp; Wasel</span>'


def agent_header(agent, state, sub=""):
    """agent: "fahem" or "wasel". sub: optional gray line, e.g. "3 matches"."""
    name = "Fahem" if agent == "fahem" else "Wasel"
    line = f'<span class="fw-agent__sub">{e(sub)}</span>' if sub else ""
    return (f'<div class="fw-agent fw-agent--{agent}"><div class="fw-agent__text">'
            f'<span class="fw-agent__name">{name}</span>{line}</div>'
            f'<span class="fw-state fw-state--{state}" role="status"><span class="fw-state__dot"></span>'
            f'{STATE_LABELS[state]}</span></div>')


def progress(n, total=11):
    segs = "".join(
        f'<span class="fw-progress__seg{" fw-progress__seg--done" if i < n - 1 else (" fw-progress__seg--now" if i == n - 1 else "")}"></span>'
        for i in range(total))
    return (f'<div class="fw-progress"><span class="fw-progress__label">Topic <b>{n} of {total}</b></span>'
            f'<div class="fw-progress__track" role="progressbar" aria-valuemin="1" aria-valuemax="{total}" aria-valuenow="{n}">{segs}</div></div>')


def quote(who, text):
    return (f'<div class="fw-quote"><span class="fw-quote__mark" aria-hidden="true">“</span>'
            f'<span><span class="fw-quote__who">{e(who)}:</span> <span class="fw-quote__text">{e(text)}</span></span></div>')


def edited():
    """Shown in place of the quote after a founder edits a field (source="edited")."""
    return '<div class="fw-quote fw-quote--edited"><span class="fw-quote__who">Edited by you</span></div>'


def field(label, value, q=None, flag="", source="interview"):
    """flag: "" or a chip label such as "Check this", "Inferred from city", "Empty"."""
    chip = f'<span class="fw-flag">{e(flag)}</span>' if flag else ''
    val = (f'<span class="fw-field__value">{e(str(value))}</span>' if value not in (None, "")
           else '<span class="fw-field__empty">Not covered in the interview.</span>')
    if source == "edited":
        qt = edited()
    else:
        qt = quote("You said", q) if q else ''
    return (f'<div class="fw-field{" fw-field--check" if flag else ""}"><div class="fw-field__head">'
            f'<span class="fw-field__label">{e(label)}</span>{chip}</div>{val}{qt}</div>')


def tag(t):
    return f'<span class="fw-tag">{e(t)}</span>'


def score(n):
    n = int(n)
    return (f'<span class="fw-score" aria-label="Fit score {n} of 100"><span class="fw-score__label">Fit</span>'
            f'<span class="fw-score__value">{n}</span></span>')


def demo_badge():
    return '<span class="fw-demo" title="Sample profile, not a real person">Demo profile</span>'


def initials(name):
    parts = [p for p in str(name).split() if p]
    return "".join(p[0] for p in parts[:2]).upper()


def match_card(name, n, tags=(), reasons=(), summary="", concern="", demo=False):
    """reasons: [(text, [(who, quote), ...]), ...]. A quote of None (edited field) is skipped.
    Put gr.Button("Request intro", variant="primary") under the card for live founders only."""
    items = "".join(
        f'<li class="fw-reason"><span class="fw-reason__text">{e(text)}</span>'
        + "".join(quote(who, q) for who, q in quotes if q) + "</li>"
        for text, quotes in reasons)
    badge = demo_badge() if demo else ""
    note = '<p class="fw-match__note">Demo profile. Intros are off for sample profiles.</p>' if demo else ""
    sub = f'<span class="fw-match__summary">{e(summary)}</span>' if summary else ""
    worry = f'<p class="fw-concern">{e(concern)}</p>' if concern else ""
    return (f'<article class="fw-match"><div class="fw-match__head">'
            f'<span class="fw-initials" aria-hidden="true">{e(initials(name))}</span>'
            f'<div class="fw-match__who"><span class="fw-match__name">{e(name)}</span>{badge}{sub}</div>{score(n)}</div>'
            f'<div class="fw-tags">{"".join(tag(t) for t in tags)}</div>'
            f'<ul class="fw-reasons">{items}</ul>{worry}{note}</article>')


def intro_card(requester, reasons=()):
    """reasons: [(text, [(who, quote), ...]), ...].
    Put Accept (variant primary) and Decline (variant secondary) under the card."""
    items = "".join(
        f'<span class="fw-reason__text">{e(text)}</span>' + "".join(quote(w, q) for w, q in quotes if q)
        for text, quotes in reasons)
    return (f'<section class="fw-intro"><span class="fw-intro__title">{e(requester)} wants an intro</span>'
            f'<span class="fw-intro__by">Wasel matched you because:</span>{items}</section>')


def contact_card(name, email):
    """Put gr.Button("Copy email", variant="secondary") under the card."""
    return ('<section class="fw-contact"><span class="fw-contact__status">'
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M5 12l5 5L19 7"/></svg>'
            f'You both said yes</span><span class="fw-contact__title">{e(name)}</span>'
            f'<dl class="fw-contact__rows"><dt>Email</dt><dd>{e(email)}</dd></dl></section>')
