"""Handshake: your AI agent meets the startup ecosystem for you.

Sections: Home (your agent's dashboard), Matches (live search), Conversations (agent-to-agent
negotiations with the verdict inline), Intros (your decisions), My agent (profile and limits).
Styling lives in ui.py; negotiation, matching and safety logic live in core/.
"""

from __future__ import annotations

import logging
import os
import queue
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import gradio as gr
from dotenv import load_dotenv

from core import matching, negotiation, profiles, storage
from core.schemas import AgentTurn, Negotiation, Profile
import ui

load_dotenv()
logging.basicConfig(level=logging.INFO)

# On the Space, sign-in is real OAuth. Locally Gradio mocks it with the account behind HF_TOKEN;
# set LOCAL_LOGIN=0 to hide the button.
LOGIN_ENABLED = bool(os.getenv("SPACE_ID")) or (bool(os.getenv("HF_TOKEN")) and os.getenv("LOCAL_LOGIN") != "0")

TZ = ZoneInfo("Asia/Qatar")
PERSONAS = [("f-layla", "Raising a $1.5M seed and needs a lead who opens doors with Gulf banks."),
            ("i-omar", "Backs seed healthtech in the GCC. Has a private valuation ceiling."),
            ("t-sara", "Senior computer vision engineer. Remote only, and won't bend on it.")]
OTHER_SIDE_DELAY = 4.0  # seconds before a sample member answers your intro request
esc = ui.esc


def go(tab_id: str):
    return gr.Tabs(selected=tab_id)


class C:
    """Component registry, filled in while the layout is built, so handlers can return {component: value}."""


def noop() -> dict:
    """An update that changes nothing (Gradio needs at least one key in a dict of updates)."""
    return {C.pending_reply: gr.skip()}


ROLE_LABEL = {"founder": "Founder", "investor": "Investor", "engineer": "Engineer", "operator": "Operator"}

ROLE_ICON = {"founder": "🚀", "investor": "💼", "engineer": "🛠️", "operator": "⚙️"}

def persona_choices() -> list[tuple[str, str]]:
    """Every seed profile, grouped by role, for the 'More demo personas' picker."""
    order = {"founder": 0, "investor": 1, "engineer": 2, "operator": 3}
    seeds = sorted(storage.seed_profiles(), key=lambda p: (order[p.role], p.display_name))
    return [(f"{ROLE_LABEL[p.role]} · {p.display_name} — {p.headline}", p.id) for p in seeds]

def person_row(p: Profile, size: str = "", sub: str | None = None) -> str:
    sub = esc(sub if sub is not None else f"{ROLE_ICON[p.role]} {ROLE_LABEL[p.role]} · {p.location}")
    return (f"<div class='who-row'>{ui.avatar(p.display_name, size)}<div class='meta'><h3>{esc(p.display_name)}</h3>"
            f"<div class='muted' style='font-size:.84rem'>{sub}</div></div></div>")

def match_card(m) -> str:
    p = m.profile
    tier = ui.chip("★ Strong match", "green") if m.fit == "strong" else ui.chip("Worth a look", "accent")
    return (f"<div class='card lift match'><div class='top'>{person_row(p)}{ui.ring(m.score)}</div>"
            f"<div style='margin-top:10px'>{tier}</div>"
            f"<p>{esc(p.headline)}</p><div class='why'><b>Why it fits</b>{esc(m.reason)}</div></div>")

FIT_CHIP = {"strong": ("✓ Strong match", "green"), "possible": ("Worth a look", "accent"), "weak": ("✗ Not a fit", "")}

def search_html(st: dict) -> str:
    """The agent's search as a live checklist: what it wants, who it scanned, what it filtered, who it checked."""
    steps = []  # (state, title, detail_html, count_html)
    active = st["active"]

    def state(name, done_when):
        return "done" if done_when else ("now" if active == name else "todo")

    if "wants" in st:
        chips = "".join(ui.chip(esc(t)) for t in st["tags"])
        steps.append((state("read", True), "Reading what you're looking for",
                      f"{ui.chip('Looking for ' + esc(st['seeking']), 'accent')}{chips}", ""))
    if "total" in st:
        steps.append((state("scan", True), "Scanning the ecosystem", "Every public profile on Handshake",
                      f"<span class='n'>{st['total']} people</span>"))
    for f in st["filters"]:
        minus = f"<span class='minus'>−{f['dropped']}</span>" if f["dropped"] else ""
        steps.append(("done", f["label"], "", f"<span class='n'>{minus}{f['kept']} left</span>"))
    if "considered" in st:
        steps.append(("done", f"Ranked {st['considered']} people by how well they fit",
                      "Comparing what you want with what each person offers", ""))
    if st.get("shortlist"):
        rows = []
        for p, score in st["shortlist"]:
            fit = st["fits"].get(p.id)
            if fit:
                label, kind = FIT_CHIP[fit[0]]
                vd = f"<div>{ui.chip(label, kind)}</div><div class='why'>{esc(fit[1])}</div>"
            else:
                vd = ui.spinner_line("Looking closely…") if active == "fit" else ""
            rows.append(f"<div class='cand {fit[0] if fit else ''}'>{ui.avatar(p.display_name, 'sm')}"
                        f"<div style='min-width:0'><div class='nm'>{esc(p.display_name)}</div>"
                        f"<div class='hl'>{esc(p.headline)}</div></div>"
                        f"<div class='bar'><i style='width:{max(6, score)}%'></i></div><div class='vd'>{vd}</div></div>")
        done_fit = len(st["fits"]) == len(st["shortlist"])
        steps.append((state("fit", done_fit), f"Looking closely at the top {len(st['shortlist'])}",
                      "Does the core need line up? Negotiable terms are left to the agents.",
                      "") + (f"<div class='cands'>{''.join(rows)}</div>",))
    body = ""
    for item in steps:
        cls, title, detail, count = item[:4]
        extra = item[4] if len(item) > 4 else ""
        mark = "✓" if cls == "done" else ""
        body += (f"<div class='sstep {cls}'><div class='ic'>{mark}</div><div><div class='t'>{title}</div>"
                 f"{'<div class=d>' + detail + '</div>' if detail else ''}{extra}</div>{count}</div>")
    if st["done"]:
        n = st["found"]
        funnel = (f"<span class='funnel'>🔎 Scanned <b>{st.get('total', 0)}</b><span class='arr'>→</span>"
                  f"<b>{st['filters'][0]['kept'] if st['filters'] else 0}</b> {esc(st.get('seeking', ''))}"
                  f"<span class='arr'>→</span><b>{len(st.get('shortlist') or [])}</b> checked closely"
                  f"<span class='arr'>→</span><b>{n}</b> worth a conversation</span>")
        return (f"<details class='search'><summary>{funnel}<span class='more'>How my agent searched ▾</span>"
                f"</summary>{body}</details>")
    return (f"<div class='search'><div class='head'><div class='spinner'></div>Your agent is searching the "
            f"ecosystem</div>{body}</div>")

LIVE_CAP = 5  # live negotiations per session

STAGE_LABELS = [("opening", "Opening"), ("exploring", "Exploring fit"), ("negotiating", "Negotiating"), ("verdict", "Verdict")]

def first(name: str) -> str:
    return esc(name.split()[0])

def progress_html(stage: str | None, finished: bool = False) -> str:
    idx = [k for k, _ in STAGE_LABELS].index(stage) if stage else -1
    parts = []
    for i, (_, label) in enumerate(STAGE_LABELS):
        done = i < idx or (finished and i <= idx)
        cls = "done" if done else "now" if i == idx else ""
        mark = "✓" if done else str(i + 1)
        if i:
            parts.append(f"<div class='line {'done' if i <= idx else ''}'></div>")
        parts.append(f"<div class='st {cls}'><div class='dot'>{mark}</div><span class='lbl'>{label}</span></div>")
    return f"<div class='stepper'>{''.join(parts)}</div>"

def transcript_html(turns: list[AgentTurn], viewer: Profile, other: Profile,
                    partial: str | None = None, typing: str | None = None, theirs: bool = False) -> str:
    rows = []
    for idx, t in enumerate(turns):
        mine = t.speaker_id == viewer.id
        who_p = viewer if mine else other
        text = partial if (partial is not None and idx == len(turns) - 1) else t.message
        who = (f"{first(viewer.display_name)}'s agent" if theirs else f"Your agent · {first(viewer.display_name)}") \
            if mine else f"{first(other.display_name)}'s agent"
        shield = ""
        if t.leak_check_passed and (partial is None or idx < len(turns) - 1):
            shield = (f"<div class='shield'>{ui.SHIELD} Protected · rewritten to keep your limit private</div>"
                      if mine and t.leak_caught else f"<div class='shield'>{ui.SHIELD} Protected</div>")
        rows.append(f"<div class='msg {'me' if mine else 'them'}'>{ui.avatar(who_p.display_name, 'sm')}"
                    f"<div class='bubble'><div class='who'>{who}</div><div dir='auto'>{esc(text)}</div>{shield}</div></div>")
    if typing == "them":
        rows.append(f"<div class='msg them'>{ui.avatar(other.display_name, 'sm')}<div class='bubble'>"
                    f"<div class='who'>{first(other.display_name)}'s agent</div>"
                    "<span class='typing'><i></i><i></i><i></i></span></div></div>")
    if not rows:
        rows.append("<div class='muted' style='text-align:center;padding:40px 0'>"
                    + ui.spinner_line("Your agent is preparing its opening…") + "</div>")
    return f"<div class='chat'>{''.join(rows)}</div>"

NEG_LANG_CHOICES = [("English", "en"), ("العربية", "fusha")]

def room_header(viewer: Profile, other: Profile, lang: str = "en", theirs: bool = False) -> str:
    topics = "".join(ui.chip(esc(t.strip())) for t in negotiation.topics_for(viewer, other).split(","))
    lang_chip = "" if lang == "en" else ui.chip(f"🗣 {negotiation.LANGUAGES[lang][0]}", "accent")
    return (f"<div class='card'><div class='room-head'><div class='versus'>{ui.avatar(viewer.display_name)}"
            f"<div><div class='eyebrow'>{'Their agent' if theirs else 'Your agent'}</div><b>{esc(viewer.display_name)}</b></div><div class='link'></div>"
            f"{ui.avatar(other.display_name)}<div><div class='eyebrow'>Meeting</div><b>{esc(other.display_name)}</b></div>"
            f"</div>{lang_chip}</div><div class='topics'>{topics}</div></div>")

VERDICT_ORDER = {"worth_meeting": 0, "maybe_later": 1, "not_fit": 2}

MINUTES_PER_FIRST_CALL = 30

def batch_header(viewer: Profile, others: list[Profile], lang: str) -> str:
    faces = "".join(ui.avatar(o.display_name) for o in others)
    lang_chip = "" if lang == "en" else ui.chip(f"🗣 {negotiation.LANGUAGES[lang][0]}", "accent")
    return (f"<div class='card'><div class='room-head'><div class='versus'>{ui.avatar(viewer.display_name)}"
            f"<div><div class='eyebrow'>Your agent</div><b>{esc(viewer.display_name)}</b></div><div class='link'></div>"
            f"<div class='faces'>{faces}</div><div><div class='eyebrow'>Meeting at once</div>"
            f"<b>{len(others)} people</b></div></div>{lang_chip}</div></div>")

def _row_status(row: dict) -> str:
    state = row["state"]
    if state == "waiting":
        return ui.chip("Waiting to start")
    if state == "talking":
        stage = dict(STAGE_LABELS).get(row["stage"] or "opening", "Opening")
        return ui.spinner_line(f"{stage} · message {row['turns']}")
    if state == "memo":
        return ui.spinner_line("Writing the deal memo…")
    if state == "failed":
        return ui.chip("Couldn't finish", "amber")
    memo_ = row["neg"].memo
    kind = {"worth_meeting": "green", "maybe_later": "amber", "not_fit": ""}[memo_.verdict]
    return f"<div class='verdict-mini'>{ui.chip(VERDICT_LABEL[memo_.verdict], kind)}{ui.ring(memo_.score)}</div>"

VERDICT_LABEL = {"worth_meeting": "Worth a meeting", "maybe_later": "Maybe later", "not_fit": "Not a fit"}

STATE_LABEL = {"waiting_you": "Waiting for you", "waiting_them": "Waiting for them", "connected": "Connected",
               "declined": "Closed", "running": "In progress"}

def _li(items: list[str], empty: str) -> str:
    return "".join(f"<li>{esc(x)}</li>" for x in items) or f"<li class='placeholder'>{esc(empty)}</li>"

def _load(neg_id: str | None, viewer_id: str | None):
    """Return (negotiation, viewer, other) or None if anything is missing."""
    if not neg_id or not viewer_id:
        return None
    neg = storage.load_negotiation(neg_id)
    if neg is None or viewer_id not in (neg.profile_a_id, neg.profile_b_id):
        return None
    other_id = neg.profile_b_id if viewer_id == neg.profile_a_id else neg.profile_a_id
    return neg, storage.get_profile(viewer_id), storage.get_profile(other_id)

MEMO_TEXT = {
    "en": {"dir": "ltr", "title": "Deal memo", "judge": "Written by a neutral judge that never saw anyone's private limits", "score": "fit score", "why": "Why", "agreed": "What was agreed",
           "open": "Still open", "ask": "Ask in the meeting", "intro": "Draft intro",
           "none_why": "No reasons given", "none_agreed": "Nothing agreed yet", "none_open": "Nothing open",
           "none_ask": "No meeting suggested", "unsent": "Nothing is sent until both of you approve.",
           "verdict": VERDICT_LABEL,
           "state": {"waiting_them": "You approved. Waiting for the other person.", "connected": "🤝 You're connected.",
                     "declined": "This thread is closed."}},
    "ar": {"dir": "rtl", "title": "مذكرة الصفقة", "judge": "كتبها حَكَم محايد لم يطّلع على الحدود الخاصة لأي طرف", "score": "درجة التوافق", "why": "الأسباب", "agreed": "ما تم الاتفاق عليه",
           "open": "نقاط ما زالت مفتوحة", "ask": "أسئلة للاجتماع", "intro": "مسودة رسالة التعارف",
           "none_why": "لا توجد أسباب", "none_agreed": "لم يتم الاتفاق على شيء بعد", "none_open": "لا توجد نقاط مفتوحة",
           "none_ask": "لا يُقترح اجتماع", "unsent": "لن يُرسل أي شيء حتى يوافق الطرفان.",
           "verdict": {"worth_meeting": "يستحق اجتماعًا", "maybe_later": "ربما لاحقًا", "not_fit": "غير مناسب"},
           "state": {"waiting_them": "وافقت. بانتظار موافقة الطرف الآخر.", "connected": "🤝 تم التواصل.",
                     "declined": "تم إغلاق هذه المحادثة."}},
}

LANG_CHOICES = [("English", "en"), ("العربية", "ar")]

def memo_html(neg: Negotiation, viewer: Profile, other: Profile, lang: str = "en") -> str:
    m = neg.memo_ar if lang == "ar" and neg.memo_ar else neg.memo
    if m is None:
        return ui.empty("📝", "The memo isn't ready", "Finish a negotiation in the Agent Room first.")
    t = MEMO_TEXT["ar" if m is neg.memo_ar else "en"]
    note = t["state"].get(negotiation.thread_state(neg, viewer.id), "")
    verdict_icon = {"worth_meeting": "✅", "maybe_later": "⏳", "not_fit": "🙅"}[m.verdict]
    pair = (f"<div class='who-row' style='gap:8px'>{ui.avatar(viewer.display_name, 'sm')}"
            f"{ui.avatar(other.display_name, 'sm')}<span class='muted' style='font-size:.85rem'>"
            f"{esc(viewer.display_name)} × {esc(other.display_name)}</span></div>")
    return (
        f"<div dir='{t['dir']}'>"
        f"<div class='memo-hero {m.verdict}'><div>{pair}<h2>{verdict_icon} {t['verdict'][m.verdict]}</h2>"
        f"<div class='muted'>{t['judge']}{' · ' + note if note else ''}</div></div>"
        f"<div style='text-align:center'>{ui.ring(m.score, 'xl')}<div class='eyebrow' style='margin-top:6px'>"
        f"{t['score']}</div></div></div>"
        "<div class='memo-grid'>"
        f"<div class='card'><h4>💡 {t['why']}</h4><ul>{_li(m.reasons, t['none_why'])}</ul></div>"
        f"<div class='card'><h4>🤝 {t['agreed']}</h4><ul>{_li(m.agreed, t['none_agreed'])}</ul></div>"
        f"<div class='card'><h4>❓ {t['open']}</h4><ul>{_li(m.open_questions, t['none_open'])}</ul></div>"
        f"<div class='card'><h4>🗓 {t['ask']}</h4><ul>{_li(m.meeting_questions, t['none_ask'])}</ul></div>"
        "</div>"
        f"<div class='letter'><div class='eyebrow'>✉️ {t['intro']}</div><p class='intro'>{esc(m.intro_message)}</p>"
        f"<div class='note'>{t['unsent']}</div></div></div>"
    )

def _memo_in(neg: Negotiation, lang: str) -> tuple[Negotiation, str]:
    """Make sure the requested language exists. Returns (negotiation, status note)."""
    if lang != "ar" or neg.memo is None or neg.memo_ar is not None:
        return neg, ""
    neg = negotiation.arabic_memo(neg)
    if neg.memo_ar is None:
        return neg, "😕 The Arabic version isn't available right now, so here's the English memo. Try again in a moment."
    return neg, ""

def _threads(viewer_id: str | None, my_negs: list[str]):
    out = []
    ids = list(my_negs or [])
    viewer = storage.get_profile(viewer_id) if viewer_id else None
    if viewer and viewer.id.startswith("u-"):  # signed-in users also see threads others started with them
        known = set(ids)
        ids = [n.id for n in storage.negotiations_for(viewer.id) if n.id not in known] + ids
    for nid in reversed(ids):
        loaded = _load(nid, viewer_id)
        if loaded and loaded[0].status == "complete":
            out.append(loaded)
    return out

ROLE_CHOICES = [("Founder", "founder"), ("Investor", "investor"), ("Engineer", "engineer"), ("Operator or joiner", "operator")]

SEEK_CHOICES = [("Investors", "investor"), ("Engineers", "engineer"), ("Operators", "operator")]

STAGE_CHOICES = [("Pre-seed", "pre-seed"), ("Seed", "seed"), ("Series A", "series a"), ("Series B", "series b")]

N_QUESTIONS = 3

def user_id(profile: gr.OAuthProfile | None) -> str | None:
    if profile is None:
        return None
    return "u-" + re.sub(r"[^a-z0-9-]", "", profile.username.lower())

def signin_note(profile: gr.OAuthProfile | None) -> str:
    if profile is not None:
        return f"✅ Signed in as **{esc(profile.username)}**. Your agent will be saved."
    if LOGIN_ENABLED:
        return ("ℹ️ You're not signed in. You can try everything, but your agent won't be saved and other people "
                "won't find you. Sign in on the **Welcome** tab to save it.")
    return "ℹ️ Sign-in is available on the Space. Here your agent lasts for this session only."

def founder_fields(role: str):
    show = role == "founder"
    return gr.CheckboxGroup(visible=show), gr.Dropdown(visible=show)

def _card_values(d: profiles.Draft | None, role: str, name: str = ""):
    """Values for the editable cards, in CARD order."""
    d = d or profiles.Draft(display_name=name)
    founder = role == "founder"
    return (d.display_name or name, d.headline, d.public_bio, d.looking_for,
            gr.CheckboxGroup(value=d.seeking if founder else [], visible=founder),
            ", ".join(d.tags), d.location,
            gr.Dropdown(value=d.stage if founder else None, visible=founder),
            profiles.terms_to_text(d.public_terms),
            "\n".join(d.private_limits), ", ".join(d.secret_terms))

def _question_boxes(questions: list[str]):
    boxes = [gr.Textbox(label=questions[i], value="", visible=True) if i < len(questions)
             else gr.Textbox(value="", visible=False) for i in range(N_QUESTIONS)]
    return [gr.Group(visible=bool(questions)), *boxes]

def build_agent(role, about, questions, a1, a2, a3, profile: gr.OAuthProfile | None):
    """Extract a draft from the description (plus any follow-up answers).

    outputs: status, questions_state, q_group, q1..q3, cards_group, CARD...
    """
    if not role:
        raise gr.Error("Choose your role first.")
    if len((about or "").strip()) < 20:
        raise gr.Error("Tell your agent a bit more about yourself: who you are and what you want.")
    name = (profile.name or profile.username) if profile else ""
    answers = {q: a for q, a in zip(questions or [], (a1, a2, a3)) if (a or "").strip()}
    try:
        draft = profiles.extract(role, about, name=name, answers=answers or None)
    except llm.LLMError:
        draft = None
    if draft is None:
        status = ("😕 The AI couldn't read that right now. You can fill in the cards below yourself, "
                  "or try again in a moment.")
        return (status, [], *_question_boxes([]), gr.Group(visible=True), *_card_values(None, role, name))
    asked = [] if answers else draft.follow_up_questions
    status = ("✨ Here's your agent. A few quick questions would make it sharper. Answer what you like, "
              "then update. Or just review the cards and activate." if asked else
              "✨ Here's your agent. Check both cards, edit anything, then activate it.")
    return (status, asked, *_question_boxes(asked), gr.Group(visible=True), *_card_values(draft, role, name))

def activate_agent(role, name, headline, bio, looking_for, seeking, tags, location, stage, terms, limits, secrets,
                   profile: gr.OAuthProfile | None):
    try:
        p = profiles.build_profile(
            profile_id=user_id(profile), role=role, display_name=name, headline=headline, public_bio=bio,
            looking_for=looking_for, seeking=seeking or [], tags=tags, location=location, stage=stage,
            public_terms=terms, private_limits=limits, secret_terms=secrets,
            hub_username=profile.username if profile else None)
    except ValueError as exc:
        raise gr.Error(str(exc))
    if profile is not None:
        storage.save_profile(p)
        note = "✅ Saved. Other people's agents can now find yours."
    else:
        storage.register_session_profile(p)
        note = "✅ Your agent is active for this session."
    return p.id, note, ", ".join(p.secret_terms)

def load_saved(profile: gr.OAuthProfile | None):
    """On page load: greet signed-in users and refill their saved agent."""
    uid = user_id(profile)
    saved = storage.get_profile(uid) if uid else None
    note = signin_note(profile)
    if saved is None:
        return (note, greet(profile), gr.Group(), gr.Radio(), *[gr.update()] * 11)
    d = profiles.Draft(**saved.model_dump(include=set(profiles.Draft.model_fields)))
    return (note + " Welcome back, your saved agent is loaded below.", greet(profile), gr.Group(visible=True),
            gr.Radio(value=saved.role), *_card_values(d, saved.role))


# =====================================================================
# Small helpers
# =====================================================================

def ago(ts: float) -> str:
    d = max(0.0, time.time() - ts)
    if d < 60:
        return "just now"
    if d < 3600:
        return f"{int(d // 60)} min ago"
    if d < 86400:
        return f"{int(d // 3600)} h ago"
    return datetime.fromtimestamp(ts, TZ).strftime("%d %b")


def greeting() -> str:
    h = datetime.now(TZ).hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def greet(profile: gr.OAuthProfile | None) -> str:
    if profile is None:
        return ""
    return ui.status(f"👋 Signed in as {esc(profile.name or profile.username)}", "ok")


def other_of(neg: Negotiation, viewer_id: str) -> Profile | None:
    return storage.get_profile(neg.profile_b_id if viewer_id == neg.profile_a_id else neg.profile_a_id)


def btn(label: str, act: str, ident: str = "", kind: str = "") -> str:
    return f"<button class='hbtn {kind}' data-act='{act}' data-id='{esc(ident)}'>{label}</button>"


def panel_html(viewer: Profile, turns: list[AgentTurn], thinking: bool = False, theirs: bool = False) -> str:
    """The vault: what this person's agent protects. theirs=True renders the other person's view."""
    limits = "".join(f"<div class='limit'>🔒 <span>{esc(x)}</span></div>" for x in viewer.private_limits) \
        or "<div class='limit muted'>No private limits set</div>"
    mine = [t for t in turns if t.speaker_id == viewer.id]
    caught = sum(t.leak_caught for t in mine)
    who = f"{first(viewer.display_name)}'s" if theirs else "your"
    meter = (ui.chip(f"{ui.SHIELD} {len(mine)} of {who} messages checked", "green")
             + (ui.chip(f"✍️ {caught} rewritten", "accent") if caught else "")) if mine else ""
    notes = [t.private_thought for t in mine if t.private_thought][-3:]
    notes_html = (f"<div class='eyebrow' style='margin-top:16px'>{who.capitalize()} agent's private notes</div>"
                  "<ul class='notes'>" + "".join(f"<li dir='auto'>{esc(n)}</li>" for n in reversed(notes))
                  + "</ul>") if notes else ""
    think = f"<div class='thinking'>{ui.spinner_line('Your agent is thinking…')}</div>" if thinking else ""
    title = f"What {first(viewer.display_name)}'s agent is protecting" if theirs else "What your agent is protecting"
    note = (f"Only {first(viewer.display_name)} sees this." if theirs
            else "Only you see this. The other agent never does.")
    return (f"<div class='vault'><h4>🔐 {title}</h4><div class='note' style='margin-top:4px'>{note}</div>"
            f"{limits}<div class='meter'>{meter}</div>{think}{notes_html}</div>")


# =====================================================================
# Home: landing (no agent yet) and dashboard (agent active)
# =====================================================================

STEPS = [
    ("✍️", "Brief your agent", "Tell it who you are, what you want, and the limits it must protect."),
    ("🔎", "It meets everyone", "It searches the ecosystem and negotiates with other people's agents."),
    ("✅", "You approve the few", "Only the conversations worth having reach you. Both sides opt in."),
]


def landing_html() -> str:
    s = storage.stats()
    steps = "".join(f"<div class='step'><div class='ico'>{ico}</div><h4>{t}</h4><p>{b}</p></div>" for ico, t, b in STEPS)
    stats = "".join(f"<div class='stat'><strong>{v}</strong><span>{k}</span></div>"
                    for k, v in (("members", s["people"]), ("agent negotiations", s["negotiations"]),
                                 ("intros made", s["intros"])))
    return ("<div class='hero'>" + ui.chip("✨ AI agents for the startup ecosystem", "accent")
            + "<h1>Your agent meets everyone.<br><span class='grad'>You meet the right few.</span></h1>"
            "<p class='lede'>Founders, investors and engineers each get an AI agent that knows their goals and their "
            "private limits. Agents talk first, so people only meet when it's worth it.</p>"
            f"<div class='steps'>{steps}</div><div class='stats'>{stats}</div></div>")


def persona_gallery() -> str:
    cards = []
    for pid, blurb in PERSONAS:
        p = storage.get_profile(pid)
        cards.append(f"<div class='card lift persona pick' data-act='persona' data-id='{pid}'>{person_row(p, 'lg')}"
                     f"<p>{esc(p.headline)}</p><p class='blurb'>{esc(blurb)}</p>"
                     f"<span class='pick-cta'>Continue as {first(p.display_name)} →</span></div>")
    return f"<div class='gallery'>{''.join(cards)}</div>"


def account_html(viewer: Profile | None) -> str:
    if viewer is None:
        return ""
    return (f"<div class='account'>{ui.avatar(viewer.display_name, 'sm')}<span class='nm'>{esc(viewer.display_name)}</span>"
            f"<span class='switch' data-act='switch' data-id=''>Switch account</span></div>")


def brand_html(viewer_id: str | None, presenter: bool) -> str:
    return ui.brand_bar(presenter=presenter, account=account_html(storage.get_profile(viewer_id) if viewer_id else None))


def _activity(viewer: Profile, threads, search: dict | None) -> list[tuple[float, str, str]]:
    events = []
    if search and search.get("viewer") == viewer.id:
        events.append((search["ts"], "🔎", f"Searched <b>{search['total']}</b> people and found "
                                          f"<b>{search['found']}</b> worth a conversation"))
    for neg, _, other in threads:
        fo = esc(first(other.display_name))
        if neg.memo:
            events.append((neg.created_at, "💬", f"Talked with {fo}'s agent · {VERDICT_LABEL[neg.memo.verdict]} "
                                                 f"· {neg.memo.score}"))
        for pid, ts in neg.decided_at.items():
            mine = pid == viewer.id
            decision = neg.decision_a if pid == neg.profile_a_id else neg.decision_b
            if mine and decision == "approved":
                events.append((ts, "✅", f"You asked to meet {fo}"))
            elif mine and decision == "declined":
                events.append((ts, "↩️", f"You passed on {fo}"))
            elif not mine and decision == "approved":
                events.append((ts, "🎉", f"{fo} said yes. You're connected"))
            elif not mine and decision == "declined":
                events.append((ts, "↩️", f"{fo} passed"))
    return sorted(events, reverse=True)[:8]


def dashboard_html(viewer_id: str | None, my_negs: list[str], search: dict | None) -> str:
    viewer = storage.get_profile(viewer_id) if viewer_id else None
    if viewer is None:
        return ""
    threads = _threads(viewer.id, my_negs)
    states = [(negotiation.thread_state(n, viewer.id), n) for n, _, _ in threads]
    waiting = [n for st, n in states if st == "waiting_you" and n.memo and n.memo.verdict != "not_fit"]
    connected = [n for st, n in states if st == "connected"]
    limits = "".join(f"<li>🔒 {esc(x)}</li>" for x in viewer.private_limits) or "<li>No private limits set</li>"
    agent = (f"<div class='card agent-card'><div class='who-row'>{ui.avatar(viewer.display_name, 'lg')}"
             f"<div class='meta'><div class='live-dot'>Your agent is active</div><h3>{esc(viewer.display_name)}</h3>"
             f"<div class='muted' style='font-size:.85rem'>{esc(viewer.headline)}</div></div></div>"
             f"<p style='margin-top:12px'><span class='muted'>Looking for</span> {esc(viewer.looking_for)}</p>"
             f"<details class='vault-mini' open><summary>🔐 Protecting {len(viewer.private_limits)} private "
             f"limit{'s' if len(viewer.private_limits) != 1 else ''} ▾</summary><ul>{limits}</ul></details>"
             "<div class='note' style='margin-top:6px'>Only you can see these. Your agent never says them.</div></div>")
    kpis = "".join(f"<div class='kpi'><strong>{v}</strong><span>{k}</span></div>" for k, v in (
        ("people scanned", search["total"] if search and search.get("viewer") == viewer.id else "–"),
        ("conversations", len(threads)), ("intros for you", len(waiting)), ("connected", len(connected))))
    if waiting:
        n = len(waiting)
        nxt = (f"<div class='next'><div><div class='eyebrow'>Up next</div><h3>{n} intro{'s' if n != 1 else ''} "
               f"need{'s' if n == 1 else ''} your decision</h3><div class='muted'>Your agent already did the first "
               f"conversation.</div></div>{btn('Review intros →', 'goto', 'intros', 'primary')}</div>")
    elif not (search and search.get("viewer") == viewer.id) and not threads:
        nxt = (f"<div class='next'><div><div class='eyebrow'>Up next</div><h3>Let your agent find people worth "
               f"meeting</h3><div class='muted'>It scans every member and checks each one closely.</div></div>"
               f"{btn('Find matches →', 'find', '', 'primary')}</div>")
    elif not threads:
        nxt = (f"<div class='next'><div><div class='eyebrow'>Up next</div><h3>Your agent found "
               f"{search['found']} {'person' if search['found'] == 1 else 'people'}</h3><div class='muted'>Send it to "
               f"talk to them. Nothing is shared until you approve.</div></div>{btn('See matches →', 'goto', 'matches', 'primary')}</div>")
    else:
        nxt = (f"<div class='next'><div><div class='eyebrow'>All caught up</div><h3>Nothing needs you right now</h3>"
               f"<div class='muted'>Your agent will keep looking.</div></div>{btn('Search again', 'find', '', '')}</div>")
    acts = _activity(viewer, threads, search)
    feed = "".join(f"<div class='ev'><span class='ic'>{ic}</span><span class='tx'>{tx}</span>"
                   f"<span class='tm'>{ago(ts)}</span></div>" for ts, ic, tx in acts) \
        or "<div class='note'>Your agent's work will show up here.</div>"
    return (f"<div class='dash-head'><div class='section-title'>{greeting()}, {esc(first(viewer.display_name))}</div>"
            f"<p class='section-sub'>Here's what your agent has been doing.</p></div>"
            f"<div class='dash-grid'><div>{agent}</div><div class='dash-right'>{nxt}<div class='kpis'>{kpis}</div>"
            f"<div class='card'><div class='eyebrow'>Activity</div><div class='feed'>{feed}</div></div></div></div>")


def agent_summary_html(viewer_id: str | None) -> str:
    viewer = storage.get_profile(viewer_id) if viewer_id else None
    if viewer is None:
        return ""
    terms = "".join(f"<div class='term'><span>{esc(k.replace('_', ' '))}</span><b>{esc(v)}</b></div>"
                    for k, v in viewer.public_terms.items()) or "<div class='note'>No public terms</div>"
    limits = "".join(f"<div class='limit'>🔒 <span>{esc(x)}</span></div>" for x in viewer.private_limits) \
        or "<div class='limit muted'>No private limits set</div>"
    tags = "".join(ui.chip(esc(t)) for t in viewer.tags)
    return (f"<div class='agent-grid'><div class='card'><div class='eyebrow'>🌐 Public profile · other agents see this"
            f"</div><div style='margin-top:10px'>{person_row(viewer, 'lg')}</div><p>{esc(viewer.public_bio)}</p>"
            f"<p><span class='muted'>Looking for</span> {esc(viewer.looking_for)}</p><div class='topics'>{tags}</div>"
            f"<div class='terms'>{terms}</div></div>"
            f"<div class='vault'><h4>🔐 Private limits</h4><div class='note' style='margin-top:4px'>Only you see these. "
            f"Your agent protects them in every conversation.</div>{limits}</div></div>")


# =====================================================================
# Conversations: list + one conversation (live chat, verdict and decision in one place)
# =====================================================================

def convo_list_html(viewer_id: str | None, my_negs: list[str], selected: str | None = None,
                    live: list[Profile] | None = None) -> str:
    viewer = storage.get_profile(viewer_id) if viewer_id else None
    if viewer is None:
        return ui.empty("💬", "No conversations yet", "Your agent's conversations will appear here.")
    rows = []
    for o in live or []:
        rows.append(f"<div class='crow live'>{ui.avatar(o.display_name, 'sm')}<div class='meta'><b>{esc(o.display_name)}</b>"
                    f"<div class='h'>{esc(o.headline)}</div></div><span class='live-pill'>● Live</span></div>")
    threads = sorted(_threads(viewer.id, my_negs), key=lambda t: -t[0].created_at)
    for neg, _, other in threads:
        verdict = neg.memo.verdict if neg.memo else "maybe_later"
        kind = {"worth_meeting": "green", "maybe_later": "amber", "not_fit": ""}[verdict]
        rows.append(f"<div class='crow {'sel' if neg.id == selected else ''}' data-act='open' data-id='{neg.id}'>"
                    f"{ui.avatar(other.display_name, 'sm')}<div class='meta'><b>{esc(other.display_name)}</b>"
                    f"<div class='h'>{ui.chip(VERDICT_LABEL[verdict], kind)} <span>{ago(neg.created_at)}</span></div>"
                    f"</div><span class='score'>{neg.memo.score if neg.memo else ''}</span></div>")
    if not rows:
        return ui.empty("💬", "No conversations yet", "Send your agent from <b>Matches</b>.")
    return f"<div class='clist'><div class='eyebrow' style='margin:2px 4px 8px'>Your agent's conversations</div>{''.join(rows)}</div>"


def decision_status_html(neg: Negotiation, viewer: Profile, other: Profile) -> str:
    state = negotiation.thread_state(neg, viewer.id)
    fo = esc(first(other.display_name))
    my_note = neg.notes.get(viewer.id)
    their_note = neg.notes.get(other.id)
    notes = ((f"<div class='msgnote'><b>Your note</b> {esc(my_note)}</div>" if my_note else "")
             + (f"<div class='msgnote'><b>{fo}'s note</b> {esc(their_note)}</div>" if their_note else ""))
    if state == "connected":
        return (f"<div class='decision done'>🎉 <div><b>You and {fo} are connected.</b><div class='muted'>The intro "
                f"is unlocked for both of you.</div>{notes}</div></div>")
    if state == "waiting_them":
        return (f"<div class='decision wait'><span class='typing'><i></i><i></i><i></i></span><div><b>Waiting for {fo}"
                f"</b><div class='muted'>You asked to meet. The intro unlocks when {fo} says yes too.</div>{notes}</div></div>")
    if state == "declined":
        return "<div class='decision'>This conversation is closed. Nothing else is shared.</div>"
    if neg.memo and neg.memo.verdict == "not_fit":
        return (f"<div class='decision'>Your agent recommends passing on {fo}. You can still ask to meet.</div>")
    return ""


def conversation_view(neg_id: str | None, viewer_id: str | None, side: str = "me", lang: str = "en") -> dict:
    """Everything the conversation pane shows for one finished negotiation."""
    loaded = _load(neg_id, viewer_id)
    if loaded is None:
        return {C.conv_empty: gr.HTML(visible=True), C.conv_detail: gr.Column(visible=False),
                C.batch_view: gr.Column(visible=False)}
    neg, me, other = loaded
    theirs = side == "them" and other.is_demo
    v, o = (other, me) if theirs else (me, other)
    if lang == "ar":
        neg, _ = _memo_in(neg, "ar")
    state = negotiation.thread_state(neg, me.id)
    can_decide = not theirs and state in ("waiting_you", "later")
    no = neg.memo is not None and neg.memo.verdict == "not_fit"
    banner = (f"<div class='their-banner'><span>👀 You're seeing <b>{esc(other.display_name)}</b>'s side of this "
              f"conversation. In a real account {esc(first(other.display_name))}'s private limits are visible only to "
              f"{esc(first(other.display_name))}.</span>{btn('Back to my side', 'myside', neg.id)}</div>") if theirs else ""
    return {
        C.conv_empty: gr.HTML(visible=False), C.conv_detail: gr.Column(visible=True),
        C.batch_view: gr.Column(visible=False), C.their_banner: banner,
        C.conv_head: room_header(v, o, neg.language, theirs=theirs),
        C.conv_progress: progress_html("verdict", finished=True),
        C.conv_chat: transcript_html(neg.turns, v, o, theirs=theirs), C.conv_panel: panel_html(v, neg.turns, theirs=theirs),
        C.conv_status: "", C.memo_section: gr.Column(visible=neg.memo is not None),
        C.memo_box: memo_html(neg, v, o, lang) if neg.memo else "",
        C.memo_lang: gr.Radio(value=lang),
        C.decide_row: gr.Row(visible=can_decide),
        C.note: gr.Textbox(visible=can_decide, value="", placeholder=f"Add a note for {first(other.display_name)} (optional)"),
        C.decision_html: "" if theirs else decision_status_html(neg, me, other),
        C.current_neg: neg.id, C.side: "them" if theirs else "me",
        # Highlight what the agent recommends: on a "not a fit" verdict, passing is the main action.
        C.approve_btn: gr.Button(value="Ask to meet anyway" if no else "Ask to meet", variant="secondary" if no else "primary"),
        C.pass_btn: gr.Button(variant="primary" if no else "secondary"),
    }


# =====================================================================
# Intros: your decisions
# =====================================================================

def intros_html(viewer_id: str | None, my_negs: list[str]) -> str:
    viewer = storage.get_profile(viewer_id) if viewer_id else None
    if viewer is None:
        return ui.empty("✉️", "No intros yet", "Intros your agent recommends will appear here.")
    groups = {"decide": [], "waiting_them": [], "connected": [], "later": [], "agent_passed": [], "declined": []}
    for neg, _, other in sorted(_threads(viewer.id, my_negs), key=lambda t: -t[0].created_at):
        state = negotiation.thread_state(neg, viewer.id)
        m = neg.memo
        if m is None:
            continue
        fo = esc(first(other.display_name))
        why = esc(m.reasons[0]) if m.reasons else ""
        if state in ("waiting_you", "later") and m.verdict == "not_fit":
            groups["agent_passed"].append(f"<div class='mini' data-act='open' data-id='{neg.id}'>{ui.avatar(other.display_name, 'sm')}"
                                          f"<div class='meta'><b>{esc(other.display_name)}</b><div class='h'>{why}</div></div></div>")
        elif state == "waiting_you":
            kind = "green" if m.verdict == "worth_meeting" else "amber"
            groups["decide"].append(
                f"<div class='card intro-card'><div class='top'>{person_row(other)}{ui.ring(m.score)}</div>"
                f"<div style='margin-top:8px'>{ui.chip(VERDICT_LABEL[m.verdict], kind)} "
                f"<span class='note'>Your agent talked with {fo}'s agent · {ago(neg.created_at)}</span></div>"
                f"<p class='why-line'>{why}</p><div class='actions'>"
                + btn("Ask to meet", "approve", neg.id, "primary") + btn("Not now", "later", neg.id)
                + btn("Pass", "pass", neg.id, "ghost") + btn("Read the conversation →", "open", neg.id, "link")
                + "</div></div>")
        elif state == "later":
            groups["later"].append(f"<div class='mini' data-act='open' data-id='{neg.id}'>{ui.avatar(other.display_name, 'sm')}"
                                   f"<div class='meta'><b>{esc(other.display_name)}</b><div class='h'>"
                                   f"{VERDICT_LABEL[m.verdict]} · {m.score}</div></div><span class='go'>Review →</span></div>")
        elif state == "waiting_them":
            groups["waiting_them"].append(
                f"<div class='card intro-card'><div class='top'>{person_row(other)}"
                f"<span class='wait-pill'><span class='typing'><i></i><i></i><i></i></span> Waiting for {fo}</span></div>"
                f"<p class='note' style='margin-top:10px'>You asked to meet {ago(neg.decided_at.get(viewer.id, neg.created_at))}. "
                f"The intro unlocks when {fo} says yes.</p></div>")
        elif state == "connected":
            ar = f"<p class='intro' dir='rtl'>{esc(neg.memo_ar.intro_message)}</p>" if neg.memo_ar else ""
            note = neg.notes.get(other.id)
            groups["connected"].append(
                f"<div class='card intro-card celebrate'><div class='top'>{person_row(other)}"
                f"<span class='pill connected'>🎉 Connected</span></div><p class='intro'>{esc(m.intro_message)}</p>{ar}"
                + (f"<div class='msgnote'><b>{fo}'s note</b> {esc(note)}</div>" if note else "")
                + "<div class='actions'>" + btn("Read the conversation →", "open", neg.id, "link")
                + (btn(f"See {fo}'s side", "theirside", neg.id, "") if other.is_demo else "") + "</div></div>")
        elif state == "declined":
            groups["declined"].append(f"<div class='mini'>{ui.avatar(other.display_name, 'sm')}<div class='meta'>"
                                      f"<b>{esc(other.display_name)}</b><div class='h'>Closed</div></div></div>")

    def section(title, items, sub=""):
        return (f"<div class='group'><h4>{title}<span class='count'>{len(items)}</span></h4>"
                f"{'<p class=note>' + sub + '</p>' if sub else ''}{''.join(items)}</div>") if items else ""

    body = (section("Needs your decision", groups["decide"])
            + section("Waiting for them", groups["waiting_them"])
            + section("Connected", groups["connected"])
            + section("Saved for later", groups["later"]))
    if groups["agent_passed"]:
        n = len(groups["agent_passed"])
        body += (f"<details class='group fold'><summary><h4>Your agent passed on {n} for you<span class='count'>{n}"
                 f"</span></h4></summary><p class='note'>A fast no saves you a meeting. Tap one to see why.</p>"
                 f"{''.join(groups['agent_passed'])}</details>")
    if groups["declined"]:
        body += (f"<details class='group fold'><summary><h4>Closed<span class='count'>{len(groups['declined'])}</span>"
                 f"</h4></summary>{''.join(groups['declined'])}</details>")
    return body or ui.empty("✉️", "No intros yet", "When your agent finds someone worth meeting, the intro lands here.")


# =====================================================================
# Refreshing everything that depends on who you are
# =====================================================================

def refresh(viewer_id, my_negs, search, presenter, selected=None) -> dict:
    has = bool(viewer_id)
    return {
        C.brand: brand_html(viewer_id, presenter),
        C.landing: gr.Column(visible=not has), C.dash: gr.Column(visible=has),
        C.dash_html: dashboard_html(viewer_id, my_negs, search),
        C.convo_list: convo_list_html(viewer_id, my_negs, selected),
        C.intros_box: intros_html(viewer_id, my_negs),
        C.agent_summary: agent_summary_html(viewer_id),
        C.matches_empty: gr.HTML(visible=not has), C.matches_body: gr.Column(visible=has),
    }


def start_as(pid, my_negs, presenter):
    """Continue as a member: land on their dashboard with a clean slate."""
    out = refresh(pid, my_negs, None, presenter)
    out.update({C.viewer_id: pid, C.match_ids: [], C.search: None, C.tabs: go("home"),
                C.search_box: "", C.no_match: gr.HTML(visible=False), C.send_all_btn: gr.Button(visible=False),
                C.picker: gr.Column(visible=False), C.agent_form: gr.Accordion(open=False),
                **{c: gr.Column(visible=False) for c in C.match_cols},
                **conversation_view(None, None)})
    return out


def switch_account(my_negs, presenter):
    out = refresh(None, my_negs, None, presenter)
    out.update({C.viewer_id: None, C.tabs: go("home"), C.picker: gr.Column(visible=True),
                C.agent_form: gr.Accordion(open=True), **conversation_view(None, None)})
    return out


# =====================================================================
# Matches: the live search
# =====================================================================

def run_search(viewer_id: str | None, presenter: bool = False):
    """Generator of {component: value}: the agent's search, step by step, then the matches."""
    viewer = storage.get_profile(viewer_id) if viewer_id else None
    if viewer is None:
        yield {C.tabs: go("matches")}
        return
    st = {"active": "read", "filters": [], "fits": {}, "done": False, "found": 0}
    hidden = {c: gr.Column(visible=False) for c in C.match_cols}
    yield {C.tabs: go("matches"), C.search_box: search_html(st), C.no_match: gr.HTML(visible=False),
           C.send_all_btn: gr.Button(visible=False), **hidden}
    frozen = matching.presenter_fits(viewer) if presenter else None
    pace, reveal = (0.75, 0.55) if presenter else (0.35, 0.28)
    matches = []
    try:
        for kind, data in matching.search(viewer, frozen_fits=frozen):
            if kind == "read":
                st.update(wants=data["wants"], tags=data["tags"], seeking=data["seeking"], active="scan")
            elif kind == "scan":
                st.update(total=data["total"], active="filter")
            elif kind == "filter":
                st["filters"].append(data)
            elif kind == "ranked":
                st.update(considered=data["considered"], shortlist=data["shortlist"], active="fit")
            elif kind == "fit":
                st["fits"][data["id"]] = (data["level"], data["reason"])
                yield {C.search_box: search_html(st)}
                time.sleep(reveal)
                continue
            elif kind == "done":
                matches = data["matches"]
                break
            yield {C.search_box: search_html(st)}
            time.sleep(pace)
    except Exception:
        logging.exception("Search failed")
    st.update(done=True, found=len(matches), active=None)
    n = len(matches)
    out = {C.search_box: search_html(st), C.match_ids: [m.profile.id for m in matches],
           C.no_match: gr.HTML(visible=not matches),
           C.send_all_btn: gr.Button(visible=n > 1, value=f"🚀 Send my agent to all {n}"),
           C.search: {"viewer": viewer.id, "total": st.get("total", 0), "found": n, "ts": time.time()}}
    for i, (col, card) in enumerate(zip(C.match_cols, C.match_cards)):
        out[col] = gr.Column(visible=i < n)
        out[card] = match_card(matches[i]) if i < n else ""
    yield out


# =====================================================================
# Sending your agent: one conversation, or everyone at once
# =====================================================================

def send_one(viewer_id, match_ids, i, live_used, lang, presenter, my_negs):
    """Generator: open the conversation pane and stream one negotiation, then the verdict and decision."""
    if not viewer_id or i >= len(match_ids):
        yield {C.tabs: go("matches")}
        return
    viewer, other = storage.get_profile(viewer_id), storage.get_profile(match_ids[i])
    lang = lang if lang in negotiation.LANGUAGES else "en"
    replaying = presenter and negotiation.has_presenter_run(viewer.id, other.id, lang)
    live = live_used < LIVE_CAP
    if live and not replaying:
        live_used += 1
    header = room_header(viewer, other, lang)
    turns: list[AgentTurn] = []
    stage = None
    talking = ui.status("💬 Agents are talking. Nothing is shared until you both approve an intro.")

    def frame(partial=None, typing=None, thinking=False, status_html=""):
        return {C.conv_head: header, C.conv_progress: progress_html(stage),
                C.conv_chat: transcript_html(turns, viewer, other, partial=partial, typing=typing),
                C.conv_panel: panel_html(viewer, turns, thinking=thinking), C.conv_status: status_html}

    first_status = (ui.status("⏳ Your agent is reading the other profile and preparing its opening…")
                    if live or replaying else ui.status("You've used this session's live conversations, so this is "
                                                        "a saved one.", "warn"))
    yield {C.tabs: go("convos"), C.conv_empty: gr.HTML(visible=False), C.conv_detail: gr.Column(visible=True),
           C.batch_view: gr.Column(visible=False), C.their_banner: "", C.memo_section: gr.Column(visible=False),
           C.convo_list: convo_list_html(viewer_id, my_negs, live=[other]), C.live_used: live_used,
           **frame(status_html=first_status)}
    result = None
    try:
        for kind, payload in negotiation.run(viewer, other, live=live, lang=lang, presenter=presenter):
            if kind == "thinking":
                mine = payload == viewer.id
                yield frame(typing=None if mine else "them", thinking=mine, status_html=talking)
            elif kind == "fallback":
                turns, stage = [], None
                yield frame(status_html=ui.status("⚡ The live AI is slow right now, so here's a saved conversation.", "warn"))
            elif kind == "turn":
                turns.append(payload)
                stage = payload.stage
                words = payload.message.split()
                for n in range(6, len(words), 6):  # typewriter effect
                    yield frame(partial=" ".join(words[:n]) + " …", status_html=talking)
                    time.sleep(0.06)
                yield frame(status_html=talking)
            elif kind == "memo":
                yield frame(status_html=ui.status("📝 Done talking. A neutral judge is writing the verdict…"))
            elif kind == "done":
                result = payload
    except Exception:
        logging.exception("Negotiation crashed")
    if result is None or result.status != "complete":
        yield {**frame(status_html=ui.status("😕 The agents couldn't finish this conversation. Please try again in "
                                             "a moment.", "warn")),
               C.convo_list: convo_list_html(viewer_id, my_negs)}
        return
    my_negs = remember_many([result.id], my_negs)
    memo_lang = "ar" if lang != "en" else "en"
    stage = "verdict"
    yield {**frame(status_html=ui.status("✅ Done. Your private limits never left your agent.", "ok")),
           C.conv_progress: progress_html("verdict", finished=True), C.memo_section: gr.Column(visible=True),
           C.memo_box: f"<div class='card' style='padding:30px'>{ui.spinner_line('Opening the verdict…')}</div>",
           C.my_negs: my_negs, C.current_neg: result.id}
    view = conversation_view(result.id, viewer_id, "me", memo_lang)
    view.pop(C.conv_chat, None)  # keep the streamed chat on screen as is
    view[C.conv_status] = ui.status("✅ Done. Your private limits never left your agent.", "ok")
    view[C.convo_list] = convo_list_html(viewer_id, my_negs, selected=result.id)
    yield view


def remember_many(ids, my_negs):
    out = list(my_negs or [])
    for nid in ids or []:
        if nid and nid not in out:
            out.append(nid)
    return out


def batch_html(viewer: Profile, rows: list[dict], done: bool) -> str:
    finished = [r for r in rows if r["state"] == "done"]
    if done and finished:
        counts = {v: sum(r["neg"].memo.verdict == v for r in finished) for v in VERDICT_ORDER}
        parts = [f"{n} {VERDICT_LABEL[v].lower()}" for v, n in counts.items() if n]
        saved = len(finished) * MINUTES_PER_FIRST_CALL
        worth = counts["worth_meeting"] + counts["maybe_later"]
        cta = btn(f"Review {worth} intro{'s' if worth != 1 else ''} →", "goto", "intros", "primary") if worth else ""
        summary = (f"<div class='card batch-summary'><div class='eyebrow'>Your agent's report</div>"
                   f"<h3>Your agent met {len(finished)} {'person' if len(finished) == 1 else 'people'}: "
                   f"{' · '.join(parts)}.</h3><div class='meter'>"
                   + ui.chip(f"⏱ Saved you about {saved // 60}h {saved % 60:02d}m of first calls" if saved >= 60
                             else f"⏱ Saved you about {saved} minutes of first calls", "accent")
                   + ui.chip(f"{ui.SHIELD} Your private limits stayed private", "green")
                   + f"</div><div class='actions' style='margin-top:12px'>{cta}</div></div>")
    else:
        active = sum(r["state"] in ("talking", "memo") for r in rows)
        summary = ui.status(f"💬 Your agent is in {active} conversation{'s' if active != 1 else ''} at once. "
                            "Nothing is shared until you approve an intro.") if active else ""
    cards = []
    for r in rows:
        clickable = r["state"] == "done"
        attrs = f" data-act='open' data-id='{r['neg'].id}'" if clickable else ""
        cards.append(f"<div class='card batch-row {'lift' if clickable else ''}'{attrs}>{person_row(r['other'])}"
                     f"<div class='batch-state'>{_row_status(r)}{'<span class=go>Open →</span>' if clickable else ''}"
                     f"</div></div>")
    return f"{summary}<div class='batch-list'>{''.join(cards)}</div>"


def send_all(viewer_id, match_ids, live_used, lang, presenter, my_negs):
    """Generator: negotiate with every match in parallel and stream a live report."""
    if not viewer_id or not match_ids:
        yield {C.tabs: go("matches")}
        return
    viewer = storage.get_profile(viewer_id)
    others = [storage.get_profile(m) for m in match_ids[:3]]
    lang = lang if lang in negotiation.LANGUAGES else "en"
    rows = [{"other": o, "state": "waiting", "turns": 0, "stage": None, "neg": None} for o in others]
    plans = []
    for o in others:
        if presenter and negotiation.has_presenter_run(viewer.id, o.id, lang):
            plans.append(False)
            continue
        live = live_used < LIVE_CAP
        live_used += live
        plans.append(live)
    yield {C.tabs: go("convos"), C.conv_empty: gr.HTML(visible=False), C.conv_detail: gr.Column(visible=False),
           C.batch_view: gr.Column(visible=True), C.batch_head: batch_header(viewer, others, lang),
           C.batch_box: batch_html(viewer, rows, False), C.live_used: live_used,
           C.convo_list: convo_list_html(viewer_id, my_negs, live=others)}
    events: queue.Queue = queue.Queue()

    def worker(i: int, other: Profile, live: bool) -> None:
        try:
            for kind, payload in negotiation.run(viewer, other, live=live, lang=lang, presenter=presenter):
                events.put((i, kind, payload))
        except Exception:
            logging.exception("Batch negotiation %d crashed", i)
        finally:
            events.put((i, "end", None))

    for i, (o, live) in enumerate(zip(others, plans)):
        threading.Thread(target=worker, args=(i, o, live), daemon=True).start()
        rows[i]["state"] = "talking"
    running = len(others)
    while running:
        try:
            i, kind, payload = events.get(timeout=120)
        except queue.Empty:
            break
        row = rows[i]
        if kind == "turn":
            row["turns"] += 1
            row["stage"] = payload.stage
        elif kind == "fallback":
            row["turns"], row["stage"] = 0, None
        elif kind == "memo":
            row["state"] = "memo"
        elif kind == "done":
            row["neg"] = payload
            row["state"] = "done" if payload.status == "complete" and payload.memo else "failed"
        elif kind == "end":
            running -= 1
            if row["state"] not in ("done", "failed"):
                row["state"] = "failed"
        if kind in ("turn", "memo", "done", "fallback"):
            yield {C.batch_box: batch_html(viewer, rows, False)}
    for r in rows:
        if r["state"] not in ("done", "failed"):
            r["state"] = "failed"
    rows.sort(key=lambda r: (r["state"] != "done",
                             VERDICT_ORDER.get(r["neg"].memo.verdict, 9) if r["state"] == "done" else 9,
                             -(r["neg"].memo.score if r["state"] == "done" else 0)))
    done = [r for r in rows if r["state"] == "done"]
    my_negs = remember_many([r["neg"].id for r in done], my_negs)
    worth = sum(r["neg"].memo.verdict != "not_fit" for r in done)
    if done:
        gr.Info(f"Your agent finished {len(done)} conversation{'s' if len(done) != 1 else ''}. "
                + (f"{worth} intro{'s' if worth != 1 else ''} need{'s' if worth == 1 else ''} you." if worth
                   else "No one worth a meeting this time."))
    yield {C.batch_box: batch_html(viewer, rows, True), C.my_negs: my_negs,
           C.convo_list: convo_list_html(viewer_id, my_negs), C.intros_box: intros_html(viewer_id, my_negs)}


# =====================================================================
# Decisions and the other side's reply
# =====================================================================

def make_decision(neg_id, viewer_id, my_negs, search, presenter, decision, note=""):
    loaded = _load(neg_id, viewer_id)
    if loaded is None:
        return noop()
    neg, me, other = loaded
    negotiation.decide(neg, me.id, decision, note)
    fo = first(other.display_name)
    if decision == "approved":
        gr.Info(f"Request sent. {fo} will see your intro.")
    elif decision == "later":
        gr.Info(f"Saved for later. {fo} won't be told.")
    else:
        gr.Info(f"Passed. {fo} won't see anything else from this conversation.")
    out = refresh(viewer_id, my_negs, search, presenter, selected=neg.id)
    out[C.pending_reply] = neg.id if decision == "approved" else None
    out[C.decision_html] = decision_status_html(storage.load_negotiation(neg.id), me, other)
    out[C.decide_row] = gr.Row(visible=False)
    out[C.note] = gr.Textbox(visible=False, value="")
    return out


def other_side_reply(pending, viewer_id, my_negs, search, presenter, current, side):
    """A sample member answers a few seconds after you ask to meet. Real members answer in their own Inbox."""
    if not pending:
        return noop()
    loaded = _load(pending, viewer_id)
    if loaded is None or not loaded[2].is_demo:
        return {C.pending_reply: None}
    time.sleep(OTHER_SIDE_DELAY)
    neg, me, other = loaded
    neg = storage.load_negotiation(neg.id) or neg
    if negotiation.thread_state(neg, me.id) != "waiting_them":
        return {C.pending_reply: None}
    yes = neg.memo is not None and neg.memo.verdict != "not_fit"
    negotiation.decide(neg, other.id, "approved" if yes else "declined",
                       note="Looking forward to it. Does next week work?" if yes else "")
    fo = first(other.display_name)
    gr.Info(f"🎉 {fo} said yes. You're connected." if yes else f"{fo} passed this time.")
    out = refresh(viewer_id, my_negs, search, presenter, selected=current)
    out[C.pending_reply] = None
    if current == neg.id and side == "me":
        out[C.decision_html] = decision_status_html(storage.load_negotiation(neg.id), me, other)
    return out


def on_list_click(evt: gr.EventData, viewer_id, my_negs, search, presenter, lang):
    act, ident = evt._data.get("act"), evt._data.get("id")
    if act == "goto":
        return {C.tabs: go(ident)}
    if act in ("open", "theirside"):
        out = conversation_view(ident, viewer_id, "them" if act == "theirside" else "me", "en")
        out[C.tabs] = go("convos")
        out[C.convo_list] = convo_list_html(viewer_id, my_negs, selected=ident)
        return out
    if act == "myside":
        return conversation_view(ident, viewer_id, "me", "en")
    if act in ("approve", "later", "pass"):
        return make_decision(ident, viewer_id, my_negs, search, presenter,
                             {"approve": "approved", "later": "later", "pass": "declined"}[act])
    return noop()


# =====================================================================
# Layout
# =====================================================================

with gr.Blocks(title="Handshake · your agent meets the ecosystem") as demo:
    C.viewer_id = gr.State(None)
    C.match_ids = gr.State([])
    C.live_used = gr.State(0)
    C.my_negs = gr.State([])
    C.search = gr.State(None)
    C.presenter = gr.State(False)  # ?demo=1 in the URL: replay saved runs at a steady pace
    C.current_neg = gr.State(None)
    C.side = gr.State("me")
    C.pending_reply = gr.State(None)

    C.brand = gr.HTML(ui.brand_bar(), js_on_load=ui.DELEGATE_JS)
    with gr.Tabs(selected="home") as tabs:
        C.tabs = tabs
        # ---------------- Home ----------------
        with gr.Tab("Home", id="home"):
            with gr.Column() as landing:
                C.landing = landing
                C.landing_html = gr.HTML(landing_html())
                with gr.Row(elem_classes="cta-row"):
                    create_btn = gr.Button("Create your agent  →", variant="primary", size="lg", scale=2)
                    if LOGIN_ENABLED:
                        gr.LoginButton(value="Sign in with Hugging Face", size="lg", scale=1)
                explore_btn = gr.Button("Or explore with a sample account", variant="secondary", size="sm",
                                        elem_classes="linkish")
                C.signed_in = gr.HTML()
                with gr.Column(visible=False) as picker:
                    C.picker = picker
                    gr.HTML("<div class='section-title' style='margin-top:6px'>Explore with a sample account</div>"
                            "<p class='section-sub'>Every sample member has a real agent with public goals and "
                            "private limits.</p>")
                    C.gallery = gr.HTML(persona_gallery(), js_on_load=ui.DELEGATE_JS)
                    with gr.Row(equal_height=False):
                        more_pick = gr.Dropdown(persona_choices(), label=f"Or search all {len(storage.seed_profiles())} "
                                                "members", value=None, filterable=True, scale=3)
                        more_btn = gr.Button("Continue", variant="primary", interactive=False, scale=1)
            with gr.Column(visible=False) as dash:
                C.dash = dash
                C.dash_html = gr.HTML(js_on_load=ui.DELEGATE_JS)

        # ---------------- Matches ----------------
        with gr.Tab("Matches", id="matches"):
            C.matches_empty = gr.HTML(ui.empty("🧭", "Set up your agent first", "Create your agent or explore with a "
                                               "sample account on <b>Home</b>."))
            with gr.Column(visible=False) as matches_body:
                C.matches_body = matches_body
                with gr.Row(equal_height=False):
                    with gr.Column(scale=3, min_width=260):
                        gr.HTML("<div class='section-title' style='margin-top:4px'>Matches for you</div>"
                                "<p class='section-sub'>Your agent searches everyone, then checks each person "
                                "closely.</p>")
                    with gr.Column(scale=2, min_width=200):
                        C.neg_lang = gr.Radio(NEG_LANG_CHOICES, value="en", label="Your agent talks in",
                                              elem_classes="seg")
                C.search_box = gr.HTML()
                C.send_all_btn = gr.Button("🚀 Send my agent to all", variant="primary", size="lg", visible=False)
                C.match_cols, C.match_cards, send_btns = [], [], []
                with gr.Row(equal_height=True):
                    for i in range(3):
                        with gr.Column(visible=False, min_width=240, elem_classes="col-card") as col:
                            C.match_cards.append(gr.HTML())
                            send_btns.append(gr.Button("Send my agent  →", variant="primary"))
                        C.match_cols.append(col)
                C.no_match = gr.HTML(ui.empty("🔭", "No obvious match yet", "Nobody fits closely enough right now. "
                                              "Try broadening what you're looking for."), visible=False)
                search_again = gr.Button("Search again", variant="secondary", size="sm", elem_classes="linkish")

        # ---------------- Conversations ----------------
        with gr.Tab("Conversations", id="convos"):
            with gr.Row(equal_height=False, elem_classes="convos"):
                with gr.Column(scale=2, min_width=250):
                    C.convo_list = gr.HTML(convo_list_html(None, []), js_on_load=ui.DELEGATE_JS)
                with gr.Column(scale=5, min_width=320):
                    C.conv_empty = gr.HTML(ui.empty("💬", "Pick a conversation", "Or send your agent from "
                                                    "<b>Matches</b> to watch a new one live."))
                    with gr.Column(visible=False) as conv_detail:
                        C.conv_detail = conv_detail
                        C.their_banner = gr.HTML(js_on_load=ui.DELEGATE_JS)
                        C.conv_head = gr.HTML()
                        with gr.Column(visible=False) as memo_section:
                            C.memo_section = memo_section
                            with gr.Row(equal_height=False, elem_classes="memo-top"):
                                gr.HTML("<div class='section-title' style='font-size:1.2rem'>The verdict</div>")
                                C.memo_lang = gr.Radio(LANG_CHOICES, value="en", show_label=False, container=False,
                                                       elem_classes="seg")
                            C.memo_box = gr.HTML()
                            C.decision_html = gr.HTML()
                            C.note = gr.Textbox(show_label=False, lines=1, max_lines=3, visible=False,
                                                placeholder="Add a note (optional)")
                            with gr.Row(visible=False) as decide_row:
                                C.decide_row = decide_row
                                approve_btn = C.approve_btn = gr.Button("Ask to meet", variant="primary", size="lg", scale=2)
                                later_btn = gr.Button("Not now", variant="secondary", size="lg", scale=1)
                                pass_btn = C.pass_btn = gr.Button("Pass", variant="secondary", size="lg", scale=1)
                        with gr.Row(equal_height=False):
                            with gr.Column(scale=3, min_width=300):
                                C.conv_progress = gr.HTML()
                                C.conv_chat = gr.HTML()
                                C.conv_status = gr.HTML()
                            with gr.Column(scale=2, min_width=240, elem_classes="sticky"):
                                C.conv_panel = gr.HTML()
                    with gr.Column(visible=False) as batch_view:
                        C.batch_view = batch_view
                        C.batch_head = gr.HTML()
                        C.batch_box = gr.HTML(js_on_load=ui.DELEGATE_JS)

        # ---------------- Intros ----------------
        with gr.Tab("Intros", id="intros"):
            gr.HTML("<div class='section-title'>Intros</div><p class='section-sub'>An intro unlocks only when both "
                    "people say yes.</p>")
            C.intros_box = gr.HTML(intros_html(None, []), js_on_load=ui.DELEGATE_JS)

        # ---------------- My agent ----------------
        with gr.Tab("My agent", id="agent"):
            C.agent_summary = gr.HTML()
            with gr.Accordion("Create your own agent", open=True) as agent_form:
                C.agent_form = agent_form
                gr.HTML("<p class='section-sub'>Describe who you are and what you want, in English or Arabic. "
                        "Mention anything your agent must protect, like a minimum salary or a maximum valuation.</p>")
                signin_md = gr.Markdown(signin_note(None))
                with gr.Column(elem_classes="form-card"):
                    role_in = gr.Radio(ROLE_CHOICES, label="I am a…")
                    about_in = gr.Textbox(
                        label="About you", lines=6, max_length=profiles.MAX_TEXT,
                        placeholder=("e.g. I'm Huda, a backend engineer in Doha with 6 years in payments. I want to "
                                     "join an early fintech as a founding engineer. Hybrid is fine. Privately, I won't "
                                     "go below $90k.\n\nأو اكتب بالعربية: أنا مؤسسة شركة ناشئة في الدوحة…"))
                    build_btn = gr.Button("✨ Build my agent", variant="primary")
                build_status = gr.Markdown()
                questions_state = gr.State([])
                with gr.Group(visible=False) as q_group:
                    with gr.Column(elem_classes="form-card"):
                        gr.HTML("<div class='eyebrow'>A few quick questions</div>")
                        q_boxes = [gr.Textbox(visible=False, lines=1) for _ in range(N_QUESTIONS)]
                        refine_btn = gr.Button("Update my agent with these answers", variant="secondary")
                with gr.Group(visible=False) as cards_group:
                    with gr.Row(equal_height=False):
                        with gr.Column(min_width=280, elem_classes="form-card"):
                            gr.HTML("<h3 style='margin:0'>🌐 Public profile</h3><div class='note'>What other agents can "
                                    "read.</div>")
                            f_name = gr.Textbox(label="Name")
                            f_headline = gr.Textbox(label="Headline")
                            f_bio = gr.Textbox(label="Bio", lines=3)
                            f_looking = gr.Textbox(label="Looking for")
                            f_seeking = gr.CheckboxGroup(SEEK_CHOICES, label="I want to meet", visible=False)
                            f_tags = gr.Textbox(label="Tags", info="Comma separated")
                            f_location = gr.Textbox(label="Location")
                            f_stage = gr.Dropdown(STAGE_CHOICES, label="Company stage", visible=False)
                            f_terms = gr.Textbox(label="Public terms", lines=4, info="One per line, like  salary: $80k–$100k")
                        with gr.Column(min_width=260, elem_classes="form-card private"):
                            gr.HTML("<h3 style='margin:0'>🔐 Private limits</h3><div class='note'>What your agent "
                                    "protects. Only you see this.</div>")
                            f_limits = gr.Textbox(label="Limits and deal-breakers", lines=5, info="One per line")
                            f_secrets = gr.Textbox(
                                label="Protected terms", info="Exact numbers and phrases the leak check blocks. "
                                "Numbers in your limits are added automatically.")
                    activate_btn = gr.Button("Activate my agent  →", variant="primary", size="lg")
                    activate_status = gr.Markdown()

    # =================================================================
    # Wiring
    # =================================================================
    ctx = [C.viewer_id, C.my_negs, C.search, C.presenter]
    everything = [C.brand, C.landing, C.dash, C.dash_html, C.convo_list, C.intros_box, C.agent_summary,
                  C.matches_empty, C.matches_body, C.viewer_id, C.match_ids, C.search, C.tabs, C.search_box,
                  C.no_match, C.send_all_btn, C.picker, C.agent_form, *C.match_cols, *C.match_cards, C.match_ids,
                  C.conv_empty, C.conv_detail, C.batch_view, C.batch_head, C.batch_box, C.their_banner, C.conv_head,
                  C.conv_progress, C.conv_chat, C.conv_panel, C.conv_status, C.memo_section, C.memo_box, C.memo_lang,
                  C.decide_row, C.note, C.decision_html, C.current_neg, C.side, C.pending_reply, C.live_used, C.my_negs,
                  C.approve_btn, C.pass_btn]
    everything = list(dict.fromkeys(everything))

    def on_brand(evt: gr.EventData, my_negs, presenter):
        if evt._data.get("act") == "switch":
            return switch_account(my_negs, presenter)
        return noop()

    C.brand.click(on_brand, inputs=[C.my_negs, C.presenter], outputs=everything, show_progress="hidden")
    create_btn.click(lambda: {C.tabs: go("agent"), C.agent_form: gr.Accordion(open=True)}, outputs=everything,
                     show_progress="hidden")
    explore_btn.click(lambda: {C.picker: gr.Column(visible=True)}, outputs=everything, show_progress="hidden")

    def on_gallery(evt: gr.EventData, my_negs, presenter):
        if evt._data.get("act") == "persona":
            return start_as(evt._data.get("id"), my_negs, presenter)
        return noop()

    C.gallery.click(on_gallery, inputs=[C.my_negs, C.presenter], outputs=everything, show_progress="hidden")
    more_pick.change(lambda pid: gr.Button(interactive=bool(pid)), inputs=more_pick, outputs=more_btn)
    more_btn.click(start_as, inputs=[more_pick, C.my_negs, C.presenter], outputs=everything, show_progress="hidden")

    def on_dash(evt: gr.EventData, viewer_id, presenter):
        act, ident = evt._data.get("act"), evt._data.get("id")
        if act == "find":
            yield from run_search(viewer_id, presenter)
        elif act == "goto":
            yield {C.tabs: go(ident)}
        else:
            yield noop()

    C.dash_html.click(on_dash, inputs=[C.viewer_id, C.presenter], outputs=everything, show_progress="hidden")
    search_again.click(run_search, inputs=[C.viewer_id, C.presenter], outputs=everything, show_progress="hidden")

    for i, b in enumerate(send_btns):
        b.click(lambda v, m, n, lang, pr, mn, i=i: (yield from send_one(v, m, i, n, lang, pr, mn)),
                inputs=[C.viewer_id, C.match_ids, C.live_used, C.neg_lang, C.presenter, C.my_negs],
                outputs=everything, show_progress="hidden", concurrency_limit=4)
    C.send_all_btn.click(send_all, inputs=[C.viewer_id, C.match_ids, C.live_used, C.neg_lang, C.presenter, C.my_negs],
                         outputs=everything, show_progress="hidden", concurrency_limit=2)

    list_inputs = [C.viewer_id, C.my_negs, C.search, C.presenter, C.neg_lang]
    reply_inputs = [C.pending_reply, C.viewer_id, C.my_negs, C.search, C.presenter, C.current_neg, C.side]
    for comp in (C.convo_list, C.intros_box, C.batch_box, C.their_banner):
        comp.click(on_list_click, inputs=list_inputs, outputs=everything, show_progress="hidden").then(
            other_side_reply, inputs=reply_inputs, outputs=everything, show_progress="hidden")

    for b, decision in ((approve_btn, "approved"), (later_btn, "later"), (pass_btn, "declined")):
        b.click(lambda n, v, m, s, pr, note, d=decision: make_decision(n, v, m, s, pr, d, note),
                inputs=[C.current_neg, C.viewer_id, C.my_negs, C.search, C.presenter, C.note],
                outputs=everything, show_progress="hidden").then(
            other_side_reply, inputs=reply_inputs, outputs=everything, show_progress="hidden")

    def on_memo_lang(lang, neg_id, viewer_id, side):
        loaded = _load(neg_id, viewer_id)
        if loaded is None:
            return noop()
        neg, me, other = loaded
        v, o = (other, me) if side == "them" else (me, other)
        neg, note = _memo_in(neg, lang)
        return {C.memo_box: memo_html(neg, v, o, lang) + (ui.status(note, "warn") if note else "")}

    C.memo_lang.input(lambda lang: {C.memo_box: f"<div class='card' style='padding:30px'>"
                                                f"{ui.spinner_line('Translating…' if lang == 'ar' else 'Switching…')}</div>"},
                      inputs=C.memo_lang, outputs=everything, show_progress="hidden").then(
        on_memo_lang, inputs=[C.memo_lang, C.current_neg, C.viewer_id, C.side], outputs=everything,
        show_progress="hidden")

    tabs.select(lambda v, m, s, pr, cur: refresh(v, m, s, pr, selected=cur),
                inputs=[*ctx, C.current_neg], outputs=everything, show_progress="hidden")

    # ---- creating your own agent ----
    card_fields = [f_name, f_headline, f_bio, f_looking, f_seeking, f_tags, f_location, f_stage, f_terms,
                   f_limits, f_secrets]
    role_in.change(founder_fields, inputs=role_in, outputs=[f_seeking, f_stage])
    build_outputs = [build_status, questions_state, q_group, *q_boxes, cards_group, *card_fields]
    build_btn.click(lambda: "⏳ Your agent is reading about you…", outputs=build_status).then(
        build_agent, inputs=[role_in, about_in, gr.State([]), *q_boxes], outputs=build_outputs)
    refine_btn.click(lambda: "⏳ Updating your agent with your answers…", outputs=build_status).then(
        build_agent, inputs=[role_in, about_in, questions_state, *q_boxes], outputs=build_outputs)
    activate_btn.click(activate_agent, inputs=[role_in, *card_fields], outputs=[C.viewer_id, activate_status, f_secrets]
                       ).success(lambda v, m, pr: {**refresh(v, m, None, pr), C.agent_form: gr.Accordion(open=False)},
                                 inputs=[C.viewer_id, C.my_negs, C.presenter], outputs=everything,
                                 show_progress="hidden"
                       ).then(run_search, inputs=[C.viewer_id, C.presenter], outputs=everything, show_progress="hidden")

    def on_load(request: gr.Request, profile: gr.OAuthProfile | None):
        presenter = request.query_params.get("demo") in ("1", "true", "yes")
        note, greeting_html, cards_vis, role_val, *cards = load_saved(profile)
        uid = user_id(profile)
        viewer = uid if uid and storage.get_profile(uid) else None
        out = refresh(viewer, [], None, presenter)
        out.update({C.presenter: presenter, C.viewer_id: viewer, C.signed_in: greeting_html, signin_md: note,
                    cards_group: cards_vis, role_in: role_val, **dict(zip(card_fields, cards)),
                    C.agent_form: gr.Accordion(open=viewer is None)})
        return out

    demo.load(on_load, outputs=list(dict.fromkeys([*everything, C.presenter, C.signed_in, signin_md, cards_group,
                                                   role_in, *card_fields])), show_progress="hidden")

demo.queue(default_concurrency_limit=4, max_size=32)

# Warm the sample accounts' matches in the background so the first search is instant.
threading.Thread(target=matching.warm, args=([pid for pid, _ in PERSONAS],), daemon=True).start()

if __name__ == "__main__":
    demo.launch(theme=ui.THEME, css=ui.CSS, head=ui.brand_theme.HEAD, js=ui.FORCE_LIGHT_JS)
