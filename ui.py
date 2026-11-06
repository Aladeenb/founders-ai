"""Handshake design system: theme, CSS, and small HTML building blocks.

Bright, calm, and consistent: white surfaces, one indigo-violet accent, soft shadows,
initials avatars, and score rings. Everything here is presentation only.
"""

from __future__ import annotations

import hashlib
import html

import gradio as gr

ACCENT = "#5b5bf6"
ACCENT_2 = "#8b5cf6"
GRADIENT = f"linear-gradient(135deg, {ACCENT} 0%, {ACCENT_2} 100%)"

THEME = gr.themes.Soft(
    primary_hue="indigo", secondary_hue="violet", neutral_hue="slate", radius_size="lg",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="#f6f7fb",
    body_text_color="#0f172a",
    body_text_color_subdued="#64748b",
    background_fill_primary="#ffffff",
    background_fill_secondary="#f8fafc",
    border_color_primary="#e6e8f0",
    color_accent=ACCENT,
    color_accent_soft="#eef0ff",
    block_background_fill="transparent",
    block_border_width="0px",
    block_shadow="none",
    block_padding="0px",
    block_label_background_fill="transparent",
    block_label_text_color="#475569",
    block_title_text_weight="600",
    panel_background_fill="transparent",
    panel_border_width="0px",
    layout_gap="14px",
    container_radius="16px",
    input_background_fill="#ffffff",
    input_border_color="#e2e5ee",
    input_border_color_focus=ACCENT,
    input_shadow_focus="0 0 0 4px rgba(91,91,246,.12)",
    input_radius="12px",
    button_large_radius="14px",
    button_medium_radius="12px",
    button_small_radius="10px",
    button_large_padding="14px 22px",
    button_primary_background_fill=GRADIENT,
    button_primary_background_fill_hover=f"linear-gradient(135deg, #4f4ff0 0%, #7c4ff0 100%)",
    button_primary_text_color="#ffffff",
    button_primary_border_color="transparent",
    button_primary_shadow="0 6px 18px rgba(91,91,246,.28)",
    button_primary_shadow_hover="0 10px 26px rgba(91,91,246,.36)",
    button_secondary_background_fill="#ffffff",
    button_secondary_background_fill_hover="#f4f5ff",
    button_secondary_border_color="#e2e5ee",
    button_secondary_text_color="#1e293b",
    checkbox_label_background_fill="#ffffff",
    checkbox_label_background_fill_selected="#eef0ff",
    checkbox_label_border_color_selected=ACCENT,
    checkbox_label_text_color_selected="#3730a3",
    loader_color=ACCENT,
    slider_color=ACCENT,
)

# Keep the app bright even when the visitor's system is in dark mode.
FORCE_LIGHT_JS = """
() => {
  const light = () => document.body.classList.remove('dark');
  light();
  new MutationObserver(light).observe(document.body, {attributes: true, attributeFilter: ['class']});
}
"""

CSS = """
:root { --hs-accent: #5b5bf6; --hs-accent-2: #8b5cf6; --hs-ink: #0f172a; --hs-muted: #64748b;
        --hs-line: #e6e8f0; --hs-soft: #f4f5ff; --hs-green: #10b981; --hs-amber: #f59e0b; --hs-slate: #64748b;
        --hs-shadow: 0 1px 2px rgba(15,23,42,.04), 0 8px 28px rgba(15,23,42,.06);
        --hs-shadow-hover: 0 2px 4px rgba(15,23,42,.05), 0 16px 40px rgba(15,23,42,.10); }
body, gradio-app { background: radial-gradient(1100px 420px at 15% -8%, rgba(139,92,246,.10), transparent 60%),
  radial-gradient(900px 380px at 95% 0%, rgba(91,91,246,.09), transparent 60%), #f6f7fb !important;
  background-attachment: fixed !important; }
.gradio-container { max-width: 1080px !important; min-width: 0 !important; width: 100% !important;
  margin: 0 auto !important; padding-top: 8px !important; background: transparent !important; }
.form { background: transparent !important; border: none !important; box-shadow: none !important; gap: 14px !important; }
.gr-accordion { background: #fff !important; border: 1px solid var(--hs-line) !important; border-radius: 16px !important;
  padding: 12px 16px !important; box-shadow: var(--hs-shadow); }
.gr-accordion .label-wrap { font-weight: 650; color: #334155; }
footer { display: none !important; }
.prose h1, .prose h2, .prose h3 { letter-spacing: -.02em; }

/* ---------- brand bar ---------- */
.brand { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 6px 2px 2px; }
.brand .logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.2rem; letter-spacing: -.02em; }
.brand .mark { width: 34px; height: 34px; border-radius: 11px; background: linear-gradient(135deg,#5b5bf6,#8b5cf6);
  display: grid; place-items: center; font-size: 18px; box-shadow: 0 6px 16px rgba(91,91,246,.35); }
.brand .mark { position: relative; }
.pdot { position: absolute; right: -2px; bottom: -2px; width: 9px; height: 9px; border-radius: 50%;
  background: #10b981; border: 2px solid #fff; }
.brand .right { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
.chip { display: inline-flex; align-items: center; gap: 6px; font-size: .74rem; font-weight: 600; padding: 4px 10px;
  border-radius: 999px; background: #fff; border: 1px solid var(--hs-line); color: #475569; white-space: nowrap; }
.chip svg { width: 12px; height: 12px; }
.chip.accent { background: var(--hs-soft); border-color: #dfe1ff; color: #3730a3; }
.chip.green { background: #ecfdf5; border-color: #c9f1e1; color: #047857; }
.chip.amber { background: #fffbeb; border-color: #fde7b0; color: #b45309; }

/* ---------- tabs as a pill stepper ---------- */
.tab-wrapper { border: none !important; margin-bottom: 10px; }
.tab-container { gap: 4px; padding: 5px; background: rgba(255,255,255,.75); border: 1px solid var(--hs-line);
  border-radius: 14px; backdrop-filter: blur(8px); box-shadow: var(--hs-shadow); width: fit-content; max-width: 100%;
  overflow-x: auto; }
.tab-container::after { display: none !important; }
.tab-container button { border-radius: 10px !important; padding: 8px 14px !important; font-weight: 600 !important;
  color: #64748b !important; border: none !important; transition: all .18s ease; }
.tab-container button:hover { color: var(--hs-ink) !important; background: #f4f5f9; }
.tab-container button.selected { background: var(--hs-soft) !important; color: #3730a3 !important; }
.tab-container button.selected::after { display: none !important; }
.tabitem { animation: hs-fade .28s ease; }
@keyframes hs-fade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

/* ---------- buttons ---------- */
button.primary, button.secondary { transition: transform .15s ease, box-shadow .2s ease, background .2s ease !important;
  font-weight: 650 !important; }
button.primary:hover:not(:disabled), button.secondary:hover:not(:disabled) { transform: translateY(-1px); }
button.secondary { box-shadow: 0 1px 2px rgba(15,23,42,.05); border: 1px solid #dcdff0 !important;
  color: #3730a3 !important; }
button:disabled { opacity: .5; }

/* ---------- surfaces ---------- */
.card { background: #fff; border: 1px solid var(--hs-line); border-radius: 18px; padding: 18px; box-shadow: var(--hs-shadow);
  transition: transform .2s ease, box-shadow .2s ease; height: 100%; box-sizing: border-box; }
.card.lift:hover { transform: translateY(-3px); box-shadow: var(--hs-shadow-hover); }
.card h3 { margin: 0; font-size: 1.05rem; letter-spacing: -.01em; }
.card p { margin: 6px 0 0; color: #334155; line-height: 1.5; }
.muted { color: var(--hs-muted); }
.eyebrow { text-transform: uppercase; font-size: .7rem; letter-spacing: .08em; font-weight: 700; color: var(--hs-muted); }
.section-title { font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; margin: 4px 0 2px; }
.section-sub { color: var(--hs-muted); margin: 0 0 6px; }
.empty { text-align: center; padding: 42px 20px; color: var(--hs-muted); background: #fff; border: 1px dashed #d9dcea;
  border-radius: 18px; }
.empty .big { font-size: 2rem; margin-bottom: 6px; }
.empty h3 { color: var(--hs-ink); margin: 0 0 4px; }
.note { font-size: .82rem; color: var(--hs-muted); }

/* avatars */
.av { width: 44px; height: 44px; border-radius: 14px; display: grid; place-items: center; color: #fff; font-weight: 750;
  font-size: .95rem; flex-shrink: 0; letter-spacing: .02em; box-shadow: inset 0 -2px 0 rgba(0,0,0,.08); }
.av.sm { width: 30px; height: 30px; border-radius: 10px; font-size: .72rem; }
.av.lg { width: 56px; height: 56px; border-radius: 18px; font-size: 1.1rem; }
.who-row { display: flex; gap: 12px; align-items: center; }
.who-row .meta { min-width: 0; }

/* ---------- welcome ---------- */
.hero { position: relative; overflow: hidden; border-radius: 26px; padding: 44px 40px 34px; background:
  radial-gradient(600px 260px at 85% 10%, rgba(139,92,246,.18), transparent 60%),
  radial-gradient(520px 260px at 0% 100%, rgba(91,91,246,.14), transparent 60%), #ffffff;
  border: 1px solid var(--hs-line); box-shadow: var(--hs-shadow); }
.hero h1 { font-size: 3rem; line-height: 1.05; letter-spacing: -.035em; margin: 14px 0 12px; font-weight: 850; max-width: 760px; }
.hero h1 .grad { background: linear-gradient(135deg,#5b5bf6,#a855f7); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero .lede { font-size: 1.15rem; color: #475569; max-width: 640px; line-height: 1.55; margin: 0; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 28px; }
.step { background: rgba(255,255,255,.8); border: 1px solid var(--hs-line); border-radius: 18px; padding: 16px; }
.step .ico { width: 36px; height: 36px; border-radius: 11px; display: grid; place-items: center; background: var(--hs-soft);
  font-size: 18px; margin-bottom: 10px; }
.step h4 { margin: 0 0 4px; font-size: .98rem; }
.step p { margin: 0; color: #475569; font-size: .9rem; line-height: 1.45; }
.stats { display: flex; gap: 10px; margin-top: 22px; flex-wrap: wrap; }
.stat { display: flex; align-items: baseline; gap: 8px; padding: 10px 16px; border-radius: 14px; background: #fff;
  border: 1px solid var(--hs-line); }
.stat strong { font-size: 1.35rem; font-weight: 800; letter-spacing: -.02em; }
.stat span { color: var(--hs-muted); font-size: .88rem; }
.cta-row { margin-top: 2px; }

/* ---------- choose ---------- */
.persona { display: flex; flex-direction: column; gap: 10px; }
.persona .blurb { font-size: .9rem; color: #475569; background: #f8fafc; border-radius: 12px; padding: 10px 12px; margin: 0; }
.persona.yourself { border: 1.5px dashed #c7c9f9; background: linear-gradient(180deg,#fbfbff,#ffffff); }
.col-card { display: flex !important; flex-direction: column; gap: 10px; }
.col-card > *:first-child { flex-grow: 1; }
.col-card > button { flex-grow: 0 !important; }
.col-card .html-container, .col-card .prose { height: 100%; }

/* ---------- discover ---------- */
.you { display: flex; justify-content: space-between; gap: 16px; align-items: center; flex-wrap: wrap; }
.vault-mini summary { cursor: pointer; font-weight: 600; font-size: .88rem; color: #3730a3; list-style: none; }
.vault-mini summary::-webkit-details-marker { display: none; }
.vault-mini ul { margin: 8px 0 0; padding: 0; list-style: none; }
.vault-mini li { font-size: .88rem; padding: 6px 10px; background: #f8fafc; border-radius: 10px; margin-top: 6px; }
.match .top { display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }
.match .why { margin-top: 12px; font-size: .9rem; color: #334155; background: linear-gradient(180deg,#f7f7ff,#fbfbff);
  border: 1px solid #ecedff; border-radius: 12px; padding: 10px 12px; line-height: 1.45; }
.match .why b { color: #3730a3; font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; display: block; margin-bottom: 2px; }
.ring { --p: 50; width: 54px; height: 54px; border-radius: 50%; flex-shrink: 0; display: grid; place-items: center;
  background: conic-gradient(var(--hs-accent) calc(var(--p) * 1%), #eceef6 0); }
.ring span { width: 42px; height: 42px; border-radius: 50%; background: #fff; display: grid; place-items: center;
  font-weight: 800; font-size: .95rem; color: var(--hs-ink); }
.ring.xl { width: 92px; height: 92px; } .ring.xl span { width: 74px; height: 74px; font-size: 1.6rem; }
.skeleton { position: relative; overflow: hidden; }
.skeleton .bar { height: 12px; border-radius: 6px; background: #eef0f5; margin-top: 10px; }
.skeleton .bar.w60 { width: 60%; } .skeleton .bar.w40 { width: 40%; } .skeleton .bar.w90 { width: 90%; }
.skeleton::after { content: ""; position: absolute; inset: 0; transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.7), transparent); animation: hs-shimmer 1.3s infinite; }
@keyframes hs-shimmer { to { transform: translateX(100%); } }
.loading-line { display: flex; align-items: center; gap: 10px; color: #3730a3; font-weight: 600; }
.spinner { width: 16px; height: 16px; border-radius: 50%; border: 2.5px solid #dfe1ff; border-top-color: var(--hs-accent);
  animation: hs-spin .8s linear infinite; }
@keyframes hs-spin { to { transform: rotate(360deg); } }
.seg .wrap { gap: 6px !important; flex-wrap: wrap; }
.seg label { padding: 6px 11px !important; font-size: .86rem !important; }
.memo-top { align-items: center !important; justify-content: space-between; }
.memo-top > *:first-child { flex-grow: 1 !important; }
.memo-top > *:last-child { flex: 0 0 230px !important; min-width: 230px !important; }
.sticky { position: sticky; top: 14px; align-self: flex-start; }

/* ---------- agent room ---------- */
.room-head { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.versus { display: flex; align-items: center; gap: 12px; }
.versus .link { width: 46px; height: 2px; background: linear-gradient(90deg,#c7c9f9,#e9d5ff); position: relative; }
.versus .link::after { content: "🤝"; position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  background: #fff; border-radius: 50%; padding: 2px; font-size: 14px; }
.topics { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.stepper { display: flex; align-items: center; margin: 2px 0 14px; }
.stepper .st { display: flex; align-items: center; gap: 8px; font-size: .82rem; font-weight: 600; color: #94a3b8; white-space: nowrap; }
.stepper .dot { width: 22px; height: 22px; border-radius: 50%; border: 2px solid #dfe2ea; background: #fff; display: grid;
  place-items: center; font-size: .7rem; color: #94a3b8; flex-shrink: 0; }
.stepper .line { flex: 1; height: 2px; background: #e6e8f0; margin: 0 8px; min-width: 12px; }
.stepper .st.done { color: #334155; } .stepper .st.done .dot { background: var(--hs-accent); border-color: var(--hs-accent); color: #fff; }
.stepper .line.done { background: var(--hs-accent); }
.stepper .st.now { color: #3730a3; } .stepper .st.now .dot { border-color: var(--hs-accent); color: var(--hs-accent);
  box-shadow: 0 0 0 5px rgba(91,91,246,.14); animation: hs-pulse 1.6s ease-in-out infinite; }
@keyframes hs-pulse { 50% { box-shadow: 0 0 0 9px rgba(91,91,246,.06); } }
.chat { display: flex; flex-direction: column; gap: 14px; min-height: 200px; padding: 18px; background: #fff;
  border: 1px solid var(--hs-line); border-radius: 20px; box-shadow: var(--hs-shadow); }
.msg { display: flex; gap: 10px; align-items: flex-end; max-width: 88%; }
.msg.me { align-self: flex-end; flex-direction: row-reverse; }
.bubble { padding: 11px 15px; border-radius: 18px; line-height: 1.5; font-size: .95rem; }
.bubble .who { font-size: .72rem; font-weight: 700; opacity: .7; margin-bottom: 3px; }
.msg.them .bubble { background: #f4f5f9; border-bottom-left-radius: 6px; color: #0f172a; }
.msg.me .bubble { background: linear-gradient(135deg,#5b5bf6,#7c5cf6); color: #fff; border-bottom-right-radius: 6px;
  box-shadow: 0 6px 18px rgba(91,91,246,.22); }
.shield svg { width: 11px; height: 11px; }
.shield { display: inline-flex; align-items: center; gap: 4px; margin-top: 7px; font-size: .68rem; padding: 2px 8px;
  border-radius: 999px; background: #e7f8f1; color: #047857; font-weight: 700; }
.msg.me .shield { background: rgba(255,255,255,.2); color: #fff; }
.typing { display: inline-flex; gap: 4px; padding: 4px 2px; }
.typing i { width: 7px; height: 7px; border-radius: 50%; background: #94a3b8; animation: hs-bounce 1.2s infinite ease-in-out; }
.typing i:nth-child(2) { animation-delay: .15s; } .typing i:nth-child(3) { animation-delay: .3s; }
@keyframes hs-bounce { 0%, 80%, 100% { transform: translateY(0); opacity: .5; } 40% { transform: translateY(-5px); opacity: 1; } }
.status { display: inline-flex; align-items: center; gap: 8px; font-size: .88rem; font-weight: 600; color: #3730a3;
  background: var(--hs-soft); border: 1px solid #dfe1ff; padding: 8px 14px; border-radius: 999px; margin-top: 12px; }
.status.ok { color: #047857; background: #ecfdf5; border-color: #c9f1e1; }
.status.warn { color: #b45309; background: #fffbeb; border-color: #fde7b0; }
.vault { background: linear-gradient(#fff,#fff) padding-box, linear-gradient(135deg,#c7c9f9,#e9d5ff) border-box;
  border: 1.5px solid transparent; border-radius: 20px; padding: 18px; box-shadow: var(--hs-shadow); }
.vault h4 { margin: 0; display: flex; align-items: center; gap: 8px; font-size: 1rem; }
.vault .limit { display: flex; gap: 10px; align-items: flex-start; padding: 10px 12px; background: #f8fafc;
  border-radius: 12px; margin-top: 8px; font-size: .9rem; }
.vault .meter { display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; }
.vault .thinking { margin-top: 12px; display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 12px;
  background: var(--hs-soft); color: #3730a3; font-size: .88rem; font-weight: 600; }
.vault .notes { margin: 6px 0 0; padding: 0; list-style: none; }
.vault .notes li { font-size: .84rem; color: #475569; padding: 6px 0; border-top: 1px dashed #e6e8f0; }

/* product shell */
.account { display: flex; align-items: center; gap: 8px; background: #fff; border: 1px solid var(--hs-line);
  border-radius: 999px; padding: 4px 6px 4px 4px; box-shadow: var(--hs-shadow); }
.account .nm { font-weight: 650; font-size: .88rem; }
.account .switch { font-size: .76rem; font-weight: 650; color: #3730a3; background: var(--hs-soft); border-radius: 999px;
  padding: 4px 10px; cursor: pointer; }
.account .switch:hover { background: #e4e6ff; }
.hbtn { font: inherit; font-weight: 650; font-size: .88rem; border-radius: 12px; padding: 9px 14px; cursor: pointer;
  border: 1px solid #dcdff0; background: #fff; color: #3730a3; transition: transform .15s ease, box-shadow .2s ease; }
.hbtn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(15,23,42,.08); }
.hbtn.primary { background: linear-gradient(135deg,#5b5bf6,#8b5cf6); color: #fff; border-color: transparent;
  box-shadow: 0 6px 18px rgba(91,91,246,.28); }
.hbtn.ghost { color: #64748b; } .hbtn.link { border-color: transparent; background: transparent; padding-left: 4px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 14px; }
button.linkish { background: transparent !important; border: none !important; box-shadow: none !important;
  color: #3730a3 !important; width: fit-content !important; margin: 0 auto; }
.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.pick { cursor: pointer; } .pick-cta { font-weight: 700; color: #3730a3; font-size: .9rem; margin-top: auto; }
.dash-grid { display: grid; grid-template-columns: minmax(280px, 1fr) minmax(320px, 1.4fr); gap: 14px; margin-top: 8px; }
.dash-right { display: flex; flex-direction: column; gap: 14px; }
.live-dot { display: inline-flex; align-items: center; gap: 6px; font-size: .74rem; font-weight: 700; color: #047857;
  text-transform: uppercase; letter-spacing: .06em; margin-bottom: 2px; }
.live-dot::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--hs-green);
  box-shadow: 0 0 0 0 rgba(16,185,129,.5); animation: hs-live 1.8s infinite; }
@keyframes hs-live { 70% { box-shadow: 0 0 0 7px rgba(16,185,129,0); } 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); } }
.next { display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap; padding: 18px 20px;
  border-radius: 20px; background: linear-gradient(135deg,#f4f5ff,#ffffff 70%); border: 1px solid #e2e4ff; box-shadow: var(--hs-shadow); }
.next h3 { margin: 4px 0 2px; font-size: 1.15rem; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.kpi { background: #fff; border: 1px solid var(--hs-line); border-radius: 16px; padding: 12px 14px; box-shadow: var(--hs-shadow); }
.kpi strong { display: block; font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; }
.kpi span { font-size: .8rem; color: var(--hs-muted); }
.feed { margin-top: 8px; } .ev { display: grid; grid-template-columns: 26px 1fr auto; gap: 8px; padding: 8px 0;
  border-top: 1px dashed #eceef4; font-size: .9rem; align-items: center; } .ev:first-child { border-top: none; }
.ev .tm { color: var(--hs-muted); font-size: .78rem; white-space: nowrap; }
.agent-grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 14px; margin-bottom: 14px; }
.terms { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 8px; margin-top: 12px; }
.term { background: #f8fafc; border-radius: 12px; padding: 8px 10px; font-size: .84rem; }
.term span { display: block; color: var(--hs-muted); font-size: .72rem; text-transform: capitalize; }
.clist { background: #fff; border: 1px solid var(--hs-line); border-radius: 20px; padding: 10px; box-shadow: var(--hs-shadow); }
.crow { display: flex; gap: 10px; align-items: center; padding: 10px; border-radius: 14px; cursor: pointer;
  transition: background .15s ease; }
.crow:hover { background: #f6f7fb; } .crow.sel { background: var(--hs-soft); }
.crow .meta { flex: 1; min-width: 0; } .crow .meta b { font-size: .9rem; }
.crow .h { font-size: .76rem; color: var(--hs-muted); display: flex; gap: 6px; align-items: center; margin-top: 2px; }
.crow .h .chip { padding: 1px 8px; font-size: .68rem; }
.crow .score { font-weight: 800; color: #334155; }
.crow.live { cursor: default; background: #f0fdf7; }
.live-pill { font-size: .72rem; font-weight: 700; color: #047857; animation: hs-blink 1.4s infinite; }
@keyframes hs-blink { 50% { opacity: .45; } }
.their-banner { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; border-radius: 16px; padding: 12px 14px;
  margin-bottom: 12px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; font-size: .9rem; }
.their-banner .hbtn { margin-left: auto; }
.decision { display: flex; gap: 12px; align-items: flex-start; margin-top: 14px; padding: 14px 16px; border-radius: 16px;
  background: #f8fafc; border: 1px solid var(--hs-line); }
.decision.done { background: #ecfdf5; border-color: #c9f1e1; } .decision.wait { background: #fffbeb; border-color: #fde7b0; }
.msgnote { margin-top: 8px; font-size: .88rem; background: #fff; border-radius: 10px; padding: 8px 10px; border: 1px solid var(--hs-line); }
.msgnote b { display: block; font-size: .72rem; color: var(--hs-muted); text-transform: uppercase; letter-spacing: .06em; }
.intro-card { margin-bottom: 12px; } .intro-card .top { display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }
.why-line { color: #334155; margin-top: 10px; }
.wait-pill { display: inline-flex; align-items: center; gap: 6px; background: #fffbeb; color: #b45309; font-weight: 700;
  font-size: .78rem; padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
.mini { display: flex; gap: 10px; align-items: center; padding: 10px 12px; background: #fff; border: 1px solid var(--hs-line);
  border-radius: 14px; margin-bottom: 8px; cursor: pointer; } .mini .meta { flex: 1; min-width: 0; }
.mini .h { font-size: .8rem; color: var(--hs-muted); } .go { font-size: .8rem; font-weight: 700; color: #3730a3; white-space: nowrap; }
details.fold > summary { list-style: none; cursor: pointer; } details.fold > summary::-webkit-details-marker { display: none; }
details.fold > summary h4::after { content: " ▾"; }
.batch-row.lift { cursor: pointer; } .batch-state { gap: 10px; }
@media (max-width: 720px) { .gallery, .dash-grid, .agent-grid { grid-template-columns: 1fr; } .kpis { grid-template-columns: repeat(2, 1fr); }
  .account .nm { display: none; } }

/* live search */
.search { background: #fff; border: 1px solid var(--hs-line); border-radius: 20px; padding: 18px 20px; box-shadow: var(--hs-shadow); }
.search .head { display: flex; align-items: center; gap: 10px; font-weight: 750; font-size: 1.02rem; margin-bottom: 6px; }
.search .head .ok { width: 22px; height: 22px; border-radius: 50%; background: var(--hs-green); color: #fff; display: grid;
  place-items: center; font-size: .75rem; }
.sstep { display: grid; grid-template-columns: 26px 1fr auto; gap: 10px; align-items: start; padding: 9px 0;
  border-top: 1px dashed #eceef4; animation: hs-fade .35s ease; }
.sstep:first-of-type { border-top: none; }
.sstep .ic { width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center; font-size: .7rem;
  border: 2px solid #dfe2ea; color: #94a3b8; background: #fff; margin-top: 1px; }
.sstep.done .ic { background: var(--hs-accent); border-color: var(--hs-accent); color: #fff; }
.sstep.now .ic { border-color: var(--hs-accent); box-shadow: 0 0 0 4px rgba(91,91,246,.14); }
.sstep.now .ic::after { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--hs-accent);
  animation: hs-pulse 1.2s infinite; }
.sstep .t { font-weight: 650; font-size: .93rem; }
.sstep .d { color: var(--hs-muted); font-size: .84rem; margin-top: 2px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.sstep .n { font-size: .78rem; font-weight: 700; color: #475569; white-space: nowrap; }
.sstep .n .minus { color: #b45309; margin-right: 6px; }
.cands { margin-top: 8px; display: flex; flex-direction: column; gap: 6px; }
.cand { display: grid; grid-template-columns: 30px minmax(120px, 1.2fr) minmax(70px, .6fr) minmax(150px, 1.4fr); gap: 10px;
  align-items: center; padding: 8px 10px; border-radius: 12px; background: #f8fafc; transition: opacity .3s ease; }
.cand .nm { font-weight: 650; font-size: .88rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cand .hl { font-size: .76rem; color: var(--hs-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cand .bar { height: 6px; border-radius: 6px; background: #e8eaf2; overflow: hidden; }
.cand .bar i { display: block; height: 100%; border-radius: 6px; background: linear-gradient(90deg,#a5a6fb,#5b5bf6); }
.cand .vd { font-size: .8rem; display: flex; flex-direction: column; gap: 2px; }
.cand .vd .why { color: #475569; font-size: .76rem; line-height: 1.35; }
.cand.weak { opacity: .5; } .cand.weak .nm { text-decoration: line-through; text-decoration-color: #cbd5e1; }
.cand.strong { background: #f0fdf7; } .cand.possible { background: #f5f5ff; }
details.search > summary { cursor: pointer; list-style: none; display: flex; align-items: center; gap: 10px; font-weight: 650; }
details.search > summary::-webkit-details-marker { display: none; }
details.search > summary .more { margin-left: auto; font-size: .8rem; color: #3730a3; font-weight: 650; }
details.search[open] > summary { margin-bottom: 8px; }
.funnel { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: .9rem; }
.funnel b { font-weight: 800; } .funnel .arr { color: #a5b4fc; }
@media (max-width: 720px) { .cand { grid-template-columns: 30px 1fr; } .cand .bar, .cand .hl { display: none; }
  .cand .vd { grid-column: 1 / -1; } }

/* batch report */
.faces { display: flex; } .faces .av { margin-left: -10px; border: 2px solid #fff; } .faces .av:first-child { margin-left: 0; }
.batch-list { display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }
.batch-row { display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap; padding: 14px 18px; }
.batch-state { display: flex; align-items: center; }
.verdict-mini { display: flex; align-items: center; gap: 10px; }
.verdict-mini .ring { width: 44px; height: 44px; } .verdict-mini .ring span { width: 34px; height: 34px; font-size: .82rem; }
.batch-summary { background: linear-gradient(135deg,#f4f5ff,#ffffff 70%); }
.batch-summary h3 { font-size: 1.25rem; margin: 6px 0 2px; }
.batch-summary .meter { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }

/* ---------- memo ---------- */
.memo-hero { display: flex; justify-content: space-between; align-items: center; gap: 18px; padding: 22px 24px;
  border-radius: 22px; border: 1px solid var(--hs-line); box-shadow: var(--hs-shadow); flex-wrap: wrap; }
.memo-hero.worth_meeting { background: linear-gradient(135deg,#ecfdf5,#ffffff 70%); }
.memo-hero.maybe_later { background: linear-gradient(135deg,#fffbeb,#ffffff 70%); }
.memo-hero.not_fit { background: linear-gradient(135deg,#f1f5f9,#ffffff 70%); }
.memo-hero > div:first-child { flex: 1 1 320px; min-width: 0; }
.memo-hero h2 { margin: 6px 0 4px; font-size: 1.9rem; letter-spacing: -.03em; font-weight: 850; }
.memo-hero.worth_meeting .ring { background: conic-gradient(var(--hs-green) calc(var(--p) * 1%), #e3f1ea 0); }
.memo-hero.maybe_later .ring { background: conic-gradient(var(--hs-amber) calc(var(--p) * 1%), #f6ecd6 0); }
.memo-hero.not_fit .ring { background: conic-gradient(var(--hs-slate) calc(var(--p) * 1%), #e7ebf0 0); }
.memo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-top: 14px; }
.memo-grid .card h4 { margin: 0 0 8px; display: flex; gap: 8px; align-items: center; font-size: .95rem; }
.memo-grid ul { padding-left: 18px; margin: 0; } .memo-grid li { margin-bottom: 6px; line-height: 1.45; color: #334155; }
.letter { margin-top: 14px; border-radius: 20px; padding: 20px 22px; background: #fff; border: 1px solid var(--hs-line);
  box-shadow: var(--hs-shadow); position: relative; }
.letter::before { content: ""; position: absolute; left: 0; top: 18px; bottom: 18px; width: 4px; border-radius: 4px;
  background: linear-gradient(#5b5bf6,#a855f7); }
.intro { white-space: pre-wrap; font-size: 1rem; line-height: 1.6; color: #1e293b; margin: 8px 0; }
.locked { filter: blur(3px); user-select: none; }
.placeholder { color: var(--hs-muted); font-style: italic; }

/* ---------- inbox ---------- */
.group h4 { margin: 18px 0 8px; font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; color: var(--hs-muted); }
.group h4 .count { background: #eef0f5; color: #475569; border-radius: 999px; padding: 1px 8px; margin-left: 6px; font-size: .72rem; }
.thread { display: flex; gap: 12px; align-items: center; background: #fff; border: 1px solid var(--hs-line);
  border-radius: 16px; padding: 12px 14px; margin-bottom: 8px; box-shadow: var(--hs-shadow); }
.thread .meta { flex: 1; min-width: 0; }
.thread .meta .h { font-size: .84rem; color: var(--hs-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pill { font-size: .72rem; padding: 3px 10px; border-radius: 999px; font-weight: 700; white-space: nowrap;
  background: #eef0f5; color: #475569; }
.pill.waiting_you { background: var(--hs-soft); color: #3730a3; }
.pill.waiting_them { background: #fffbeb; color: #b45309; }
.pill.connected { background: #ecfdf5; color: #047857; }
.celebrate { background: linear-gradient(135deg,#ecfdf5,#ffffff 70%); }
.celebrate .big { font-size: 2.2rem; }

/* ---------- forms ---------- */
.form-card { background: #fff; border: 1px solid var(--hs-line); border-radius: 20px; padding: 18px !important;
  box-shadow: var(--hs-shadow); }
.form-card.private { background: linear-gradient(#fff,#fff) padding-box, linear-gradient(135deg,#c7c9f9,#e9d5ff) border-box;
  border: 1.5px solid transparent; }

@media (max-width: 720px) {
  .gradio-container { padding-left: 12px !important; padding-right: 12px !important; }
  .tab-container { width: 100%; }
  .memo-hero h2 { font-size: 1.5rem; }
  .hero { padding: 28px 20px 22px; } .hero h1 { font-size: 2.1rem; }
  .steps { grid-template-columns: 1fr; }
  .msg { max-width: 96%; }
  .stepper .st span.lbl { display: none; }
  .brand .right .chip.hide-sm { display: none; }
}
"""


# ---------------- building blocks ----------------

_PALETTE = [("#5b5bf6", "#8b5cf6"), ("#0ea5e9", "#6366f1"), ("#10b981", "#0ea5e9"), ("#f59e0b", "#ef4444"),
            ("#ec4899", "#8b5cf6"), ("#14b8a6", "#22c55e"), ("#f97316", "#ec4899"), ("#6366f1", "#06b6d4")]


def esc(text: str | None) -> str:
    return html.escape(text or "")


def initials(name: str) -> str:
    parts = [p for p in (name or "?").replace("-", " ").split() if p[:1].isalpha()]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def avatar(name: str, size: str = "") -> str:
    a, b = _PALETTE[int(hashlib.md5((name or "").encode()).hexdigest(), 16) % len(_PALETTE)]
    return (f"<div class='av {size}' style='background:linear-gradient(135deg,{a},{b})'>"
            f"{esc(initials(name))}</div>")


def ring(score: int, size: str = "") -> str:
    return f"<div class='ring {size}' style='--p:{max(0, min(100, score))}'><span>{score}</span></div>"


def chip(text: str, kind: str = "", extra: str = "") -> str:
    return f"<span class='chip {kind} {extra}'>{text}</span>"


def empty(icon: str, title: str, body: str) -> str:
    return f"<div class='empty'><div class='big'>{icon}</div><h3>{title}</h3><div>{body}</div></div>"


def status(text: str, kind: str = "") -> str:
    return f"<div class='status {kind}'>{text}</div>" if text else ""


def spinner_line(text: str) -> str:
    return f"<div class='loading-line'><div class='spinner'></div>{text}</div>"


def skeleton_card() -> str:
    return ("<div class='card skeleton'><div class='who-row'><div class='av' style='background:#eef0f5'></div>"
            "<div style='flex:1'><div class='bar w60'></div><div class='bar w40'></div></div></div>"
            "<div class='bar w90' style='margin-top:18px'></div><div class='bar w60'></div>"
            "<div class='bar w90' style='margin-top:18px;height:46px'></div></div>")


def brand_bar(presenter: bool = False, account: str = "") -> str:
    # In presenter mode a small green dot on the logo tells the presenter replays are on; the audience won't notice.
    dot = "<span class='pdot' title='Presenter mode'></span>" if presenter else ""
    return (f"<div class='brand'><div class='logo'><div class='mark'>🤝{dot}</div>Handshake</div>"
            "<div class='right'>" + (account or chip("Qai × Hugging Face · Doha", "", "hide-sm")) + "</div></div>")


# Rich HTML lists (intros, conversations, dashboard) report clicks on [data-act] elements back to Python.
# Delegation on the container survives every re-render of the HTML inside it.
DELEGATE_JS = """
element.addEventListener('click', (e) => {
  const t = e.target.closest('[data-act]');
  if (!t || !element.contains(t)) return;
  if (t.tagName === 'SUMMARY') return;
  e.preventDefault();
  trigger('click', {act: t.dataset.act, id: t.dataset.id || ''});
});
"""


SHIELD = ("<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.6' stroke-linecap='round' "
          "stroke-linejoin='round'><path d='M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3z'/>"
          "<path d='M8.5 12l2.5 2.5 4.5-5'/></svg>")
