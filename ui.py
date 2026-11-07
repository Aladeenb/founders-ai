"""Handshake design system: a majlis in daylight.

Pearl-white ground with warm sand glows and a faint khatam (eight-point star) lattice, gold Ruqaa calligraphy
that writes itself right to left, Instrument Serif display type and white glass panels with a warm spotlight
that follows the cursor. Qatar maroon carries actions; gold carries ornament. The logo is two halves joined
along the serrated edge of the Qatari flag.

Every effect switches off under prefers-reduced-motion. Everything here is presentation only.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import gradio as gr
from gradio.themes.utils import colors, sizes

ASSETS = Path(__file__).parent / "brand" / "assets"
gr.set_static_paths(paths=[ASSETS])
FAVICON = str(ASSETS / "handshake-mark.svg")

UI_FONT = '"Geist", "IBM Plex Sans Arabic", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'

ACCENT_GRAD = "linear-gradient(180deg,#b72a55 0%,#8a1538 55%,#6e0f2b 100%)"
GOLD_GRAD = "linear-gradient(180deg,#f3d491 0%,#d6a14a 55%,#b07a2a 100%)"

THEME = gr.themes.Base(
    primary_hue=colors.rose,
    secondary_hue=colors.stone,
    neutral_hue=colors.stone,
    text_size=sizes.text_md,
    spacing_size=sizes.spacing_md,
    radius_size=sizes.radius_lg,
    font=[gr.themes.GoogleFont("Geist"), gr.themes.GoogleFont("IBM Plex Sans Arabic"), gr.themes.Font("sans-serif")],
).set(
    body_background_fill="#fbf8f3",
    body_text_color="#1f1418",
    body_text_color_subdued="#7a6c66",
    background_fill_primary="#ffffff",
    background_fill_secondary="#f8f4ee",
    block_background_fill="transparent",
    block_border_width="0px",
    block_shadow="none",
    block_padding="0px",
    block_label_background_fill="transparent",
    block_label_text_color="#4a3d40",
    block_title_text_color="#4a3d40",
    block_title_text_weight="500",
    block_title_text_size="13px",
    block_info_text_color="#7a6c66",
    block_info_text_size="12px",
    border_color_primary="rgba(60,20,30,.10)",
    input_background_fill="#ffffff",
    input_background_fill_focus="#ffffff",
    input_border_color="rgba(60,20,30,.14)",
    input_border_color_hover="rgba(60,20,30,.26)",
    input_border_color_focus="#8a1538",
    input_border_width="1px",
    input_shadow="0 1px 2px rgba(60,20,30,.04)",
    input_shadow_focus="0 0 0 4px rgba(138,21,56,.10)",
    input_radius="14px",
    input_placeholder_color="#b3a69c",
    button_primary_background_fill=ACCENT_GRAD,
    button_primary_background_fill_hover=ACCENT_GRAD,
    button_primary_text_color="#ffffff",
    button_primary_text_color_hover="#ffffff",
    button_primary_border_color="transparent",
    button_secondary_background_fill="#ffffff",
    button_secondary_background_fill_hover="#fdf7f8",
    button_secondary_text_color="#1f1418",
    button_secondary_text_color_hover="#8a1538",
    button_secondary_border_color="rgba(60,20,30,.14)",
    button_large_radius="999px",
    button_medium_radius="999px",
    button_small_radius="999px",
    button_large_text_weight="600",
    button_medium_text_weight="600",
    button_primary_shadow="none",
    button_primary_shadow_hover="none",
    button_primary_shadow_active="none",
    button_secondary_shadow="none",
    button_secondary_shadow_hover="none",
    button_secondary_shadow_active="none",
    checkbox_label_background_fill="#ffffff",
    checkbox_label_background_fill_hover="#f8f4ee",
    checkbox_label_background_fill_selected="#8a1538",
    checkbox_label_text_color="#1f1418",
    checkbox_label_text_color_selected="#ffffff",
    checkbox_label_border_color="rgba(60,20,30,.14)",
    checkbox_label_border_width="1px",
    checkbox_background_color="#ffffff",
    checkbox_background_color_selected="#8a1538",
    checkbox_border_color_selected="#8a1538",
    color_accent="#8a1538",
    color_accent_soft="rgba(138,21,56,.08)",
    link_text_color="#8a1538",
    link_text_color_hover="#6e0f2b",
)

HEAD = (
    '<meta name="theme-color" content="#fbf8f3">'
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Aref+Ruqaa:wght@400;700'
    '&family=Geist:wght@300..700&family=IBM+Plex+Sans+Arabic:wght@400;500;600'
    '&family=Instrument+Serif:ital@0;1&family=Reem+Kufi:wght@400..700&display=swap">'
)

# Runs once on load: keeps gradio's own theme in its light slot (our palette lives there), builds the
# sliding gold dock indicator and Arabic tab labels, counts numbers up, and moves the card spotlight.
FORCE_LIGHT_JS = r"""
() => {
  const light = () => document.body.classList.remove('dark');
  light();
  new MutationObserver(light).observe(document.body, {attributes: true, attributeFilter: ['class']});
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const AR = {home: 'الرئيسية', matches: 'التوافق', convos: 'الحوارات', intros: 'التعارف', agent: 'وكيلي'};
  const dock = () => document.querySelectorAll('.tab-container[role=tablist]').forEach((tl) => {
    let ind = tl.querySelector('.hs-ind');
    if (!ind) { ind = document.createElement('span'); ind.className = 'hs-ind'; tl.prepend(ind); tl.classList.add('has-ind'); }
    tl.querySelectorAll('button[role=tab]').forEach((b) => { const a = AR[b.dataset.tabId]; if (a && b.dataset.ar !== a) b.dataset.ar = a; });
    const sel = tl.querySelector('button.selected');
    if (sel) { ind.style.width = sel.offsetWidth + 'px'; ind.style.transform = `translateX(${sel.offsetLeft}px)`; ind.style.opacity = 1; }
  });
  const count = () => document.querySelectorAll('[data-count]:not([data-done])').forEach((el) => {
    el.dataset.done = '1';
    const to = parseFloat(el.dataset.count);
    if (reduce || !isFinite(to)) { el.textContent = el.dataset.count; return; }
    const t0 = performance.now(), d = 1100;
    const step = (t) => { const k = Math.min(1, (t - t0) / d); const e = k >= 1 ? 1 : 1 - Math.pow(2, -10 * k);
      el.textContent = Math.round(to * e); if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });
  let raf = 0;
  const follow = () => document.querySelectorAll('.chat.live').forEach((c) => { c.style.scrollBehavior = 'auto'; c.scrollTop = c.scrollHeight; });
  const tick = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => { dock(); count(); follow(); }); };
  new MutationObserver(tick).observe(document.body, {subtree: true, childList: true, attributes: true, attributeFilter: ['class']});
  addEventListener('resize', tick);
  document.fonts && document.fonts.ready.then(tick);
  tick();
  const SPOT = '.card,.person,.search,.verdict,.col-card,.rows,.batch-list,.vault,.form-card';
  document.addEventListener('pointermove', (e) => {
    const c = e.target.closest && e.target.closest(SPOT);
    if (!c) return;
    const r = c.getBoundingClientRect();
    c.style.setProperty('--mx', (e.clientX - r.left) + 'px');
    c.style.setProperty('--my', (e.clientY - r.top) + 'px');
  }, {passive: true});
}
"""

# ---------------------------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------------------------

_KHATAM_TILE = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'%3E"
                "%3Cg fill='none' stroke='%238a1538' stroke-opacity='.07' stroke-width='.8'%3E"
                "%3Crect x='19' y='19' width='26' height='26'/%3E"
                "%3Crect x='19' y='19' width='26' height='26' transform='rotate(45 32 32)'/%3E"
                "%3Cpath d='M0 32h6M58 32h6M32 0v6M32 58v6'/%3E%3C/g%3E%3C/svg%3E")
_GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E"
          "%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E"
          "%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.55'/%3E%3C/svg%3E")

TOKENS = """
:root {
  --n0: #ffffff; --n1: #fbf8f3; --n2: #f6f0e8; --n3: #efe6da;
  --pearl: #1f1418; --pearl-2: #4a3d40; --muted: #7a6c66; --faint: #b3a69c;
  --line: rgba(60,20,30,.08); --line-2: rgba(60,20,30,.14);
  --gold: #94671d; --gold-orn: #c99a45; --gold-hi: #fbe3ae; --gold-lo: #b07a2a;
  --maroon: #8a1538; --maroon-hi: #b72a55; --rose: #b3264f;
  --green: #23824c; --amber: #a86d12;
  --glass: linear-gradient(180deg, rgba(255,255,255,.92), rgba(255,255,255,.72));
  --shadow: 0 1px 2px rgba(60,20,30,.04), 0 14px 36px -18px rgba(60,20,30,.18);
  --shadow-hi: 0 2px 4px rgba(60,20,30,.04), 0 28px 60px -24px rgba(60,20,30,.28);
  --accent-grad: ACCENT_GRAD; --gold-grad: GOLD_GRAD;
  --gold-text: linear-gradient(100deg, #9a6a1c 0%, #d9a649 28%, #b07a2a 48%, #e9c47c 62%, #9a6a1c 100%);
  --ease: cubic-bezier(.2,.8,.2,1); --spring: cubic-bezier(.34,1.45,.5,1);
  --r: 18px; --r-lg: 24px;
  --ui: UI_FONT; --serif: "Instrument Serif", "Times New Roman", serif;
  --kufi: "Reem Kufi", "IBM Plex Sans Arabic", sans-serif; --ruqaa: "Aref Ruqaa", "Reem Kufi", serif;
}
"""

GRADIO_CSS = """
html, body, gradio-app { background: var(--n1) !important; }
body { min-height: 100vh; }
body::before { content: ""; position: fixed; inset: -20%; z-index: 0; pointer-events: none;
  background:
    radial-gradient(40% 36% at 84% 4%, rgba(183,42,85,.10), transparent 70%),
    radial-gradient(36% 32% at 6% 30%, rgba(214,160,70,.16), transparent 70%),
    radial-gradient(46% 40% at 50% 112%, rgba(214,160,70,.10), transparent 70%);
  animation: hs-drift 26s ease-in-out infinite alternate; }
body::after { content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image: url("KHATAM"), url("GRAIN"); background-size: 64px 64px, 160px 160px;
  mix-blend-mode: multiply; opacity: .55;
  -webkit-mask-image: radial-gradient(120% 80% at 50% 0%, #000 0%, rgba(0,0,0,.35) 55%, transparent 100%);
          mask-image: radial-gradient(120% 80% at 50% 0%, #000 0%, rgba(0,0,0,.35) 55%, transparent 100%); }
gradio-app, body .gradio-container { position: relative; z-index: 1; }
body .gradio-container {
  --font: UI_FONT; --body-text-size: 15px; --layout-gap: 18px;
  font-family: UI_FONT !important; color: var(--pearl); font-size: 15px;
  max-width: 1120px !important; width: 100% !important; min-width: 0 !important;
  margin: 0 auto !important; padding: 0 32px 96px !important; background: transparent !important;
  -webkit-font-smoothing: antialiased; }
body .gradio-container ::selection { background: rgba(138,21,56,.35); color: #fff; }
body .gradio-container .main, body .gradio-container .wrap.app { padding: 0 !important; }
footer { display: none !important; }
body .gradio-container .form { background: transparent !important; border: 0 !important; box-shadow: none !important;
  gap: 16px !important; overflow: visible !important; }
body .gradio-container .block { overflow: visible; }
body .gradio-container .block.padded { padding: 0 !important; }
body .gradio-container .html-container { padding: 0 !important; }

/* ---------- the dock: floating glass nav, gold pill slides between tabs ---------- */
body .gradio-container .tab-wrapper { position: sticky !important; top: 14px; z-index: 60; width: fit-content !important;
  max-width: 100%; margin: -62px auto 44px !important; padding: 5px !important; height: auto !important;
  border: 1px solid var(--line-2) !important; border-radius: 999px !important;
  background: rgba(255,255,255,.72) !important; backdrop-filter: blur(20px) saturate(150%); -webkit-backdrop-filter: blur(20px) saturate(150%);
  box-shadow: 0 1px 2px rgba(60,20,30,.05), 0 18px 44px -20px rgba(60,20,30,.30), inset 0 1px 0 #fff !important; }
body .gradio-container .tab-container[role=tablist] { position: relative; gap: 2px !important; height: auto !important;
  padding: 0 !important; background: none !important; border: 0 !important; box-shadow: none !important; overflow: visible; }
body .gradio-container .tab-container::after { display: none !important; }
body .gradio-container .tab-container .hs-ind { position: absolute; top: 0; left: 0; height: 100%; width: 0; opacity: 0;
  border-radius: 999px; background: var(--accent-grad); z-index: 0; pointer-events: none;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.28), 0 8px 22px -8px rgba(138,21,56,.55);
  transition: transform .55s var(--spring), width .55s var(--spring), opacity .3s; }
body .gradio-container .tab-container[role=tablist] button { position: relative; z-index: 1; display: flex !important;
  flex-direction: column; align-items: center; justify-content: center; gap: 1px; padding: 7px 18px 6px !important;
  margin: 0 !important; border: 0 !important; border-radius: 999px !important; background: none !important; height: auto !important;
  color: var(--pearl-2) !important; font-family: UI_FONT !important; font-size: 13px !important; font-weight: 500 !important;
  line-height: 1.2; white-space: nowrap; transition: color .3s var(--ease); }
body .gradio-container .tab-container[role=tablist] button::after { content: attr(data-ar) !important; display: block !important;
  position: static !important; height: auto !important; width: auto !important; background: none !important; transform: none !important;
  font-family: var(--kufi); font-size: 10px; font-weight: 500; color: var(--gold); opacity: .75; line-height: 1.2; }
body .gradio-container .tab-container[role=tablist] button:hover { color: var(--pearl) !important; }
body .gradio-container .tab-container[role=tablist] button.selected { color: #fff !important; font-weight: 600 !important; }
body .gradio-container .tab-container[role=tablist] button.selected::after { color: var(--gold-hi); opacity: 1; }
body .gradio-container .tab-container[role=tablist]:not(.has-ind) button.selected { background: var(--accent-grad) !important; }
/* gradio folds tabs into a menu by measuring this hidden copy; keep it tiny so every tab stays in the dock */
body .gradio-container .tab-container.visually-hidden button { padding: 0 !important; font-size: 1px !important; }
body .gradio-container .overflow-menu { display: none !important; }
body .gradio-container .overflow-menu > button { border-radius: 999px; padding: 8px 12px; color: var(--pearl-2); }
body .gradio-container .overflow-dropdown { background: #fff !important; border: 1px solid var(--line-2) !important;
  border-radius: 16px !important; box-shadow: var(--shadow-hi) !important; padding: 6px !important; z-index: 80 !important; }
body .gradio-container .overflow-dropdown button { border-radius: 10px !important; padding: 8px 12px !important; color: var(--pearl) !important; }
body .gradio-container .overflow-dropdown button:hover { background: rgba(138,21,56,.06) !important; }
body .gradio-container .tabitem { padding: 0 !important; border: 0 !important; background: none !important; }

/* ---------- buttons: gold pills with a light sweep, glass secondaries that glow ---------- */
body .gradio-container button.primary, body .gradio-container button.secondary {
  position: relative; overflow: hidden; isolation: isolate; font-family: UI_FONT !important; font-weight: 600 !important;
  font-size: 14px !important; letter-spacing: -.005em; border-radius: 999px !important; min-height: 44px;
  padding: 10px 22px !important;
  transition: transform .25s var(--spring), box-shadow .3s var(--ease), border-color .3s var(--ease),
              background .3s var(--ease), color .3s var(--ease) !important; }
body .gradio-container button.primary { border: 0 !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.28), inset 0 -2px 0 rgba(60,5,20,.25), 0 12px 28px -12px rgba(138,21,56,.55),
              0 0 0 1px rgba(110,15,43,.2) !important; }
body .gradio-container button.primary::after { content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none;
  background: linear-gradient(105deg, transparent 30%, rgba(255,236,190,.38) 48%, transparent 66%);
  transform: translateX(-130%); transition: transform .9s var(--ease); }
body .gradio-container button.primary:hover:not(:disabled) { transform: translateY(-2px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.28), inset 0 -2px 0 rgba(60,5,20,.25), 0 18px 40px -12px rgba(138,21,56,.65),
              0 0 0 1px rgba(110,15,43,.25) !important; }
body .gradio-container button.primary:hover:not(:disabled)::after { transform: translateX(130%); }
body .gradio-container button.cta::after { animation: hs-sweep 4.5s var(--ease) infinite 1.2s; }
body .gradio-container button.secondary { border: 1px solid var(--line-2) !important; backdrop-filter: blur(10px); }
body .gradio-container button.secondary:hover:not(:disabled) { border-color: rgba(138,21,56,.55) !important;
  box-shadow: 0 0 0 4px rgba(138,21,56,.08), 0 10px 30px -14px rgba(138,21,56,.6) !important; transform: translateY(-1px); }
body .gradio-container button.primary:active:not(:disabled),
body .gradio-container button.secondary:active:not(:disabled) { transform: scale(.97); }
body .gradio-container button.lg { min-height: 52px; padding: 12px 28px !important; font-size: 15px !important; }
body .gradio-container button.sm { min-height: 34px; padding: 6px 14px !important; font-size: 13px !important; }
body .gradio-container button:disabled { opacity: .35; cursor: default; }
body .gradio-container button.linkish { background: none !important; border: 0 !important; box-shadow: none !important;
  min-height: 0; padding: 6px 0 !important; width: fit-content !important; color: var(--muted) !important;
  font-size: 13px !important; font-weight: 500 !important; }
body .gradio-container button.linkish::after { display: none; }
body .gradio-container button.linkish:hover { color: var(--maroon) !important; transform: none !important; }
body .gradio-container .row-auto { gap: 12px !important; flex-wrap: wrap; align-items: center; }
body .gradio-container .row-auto > button, body .gradio-container .row-auto > .block { flex: 0 0 auto !important;
  min-width: 0 !important; width: auto !important; }

/* ---------- inputs ---------- */
body .gradio-container textarea, body .gradio-container input[type=text], body .gradio-container input[type=search] {
  font-family: UI_FONT !important; font-size: 15px !important; line-height: 1.6 !important; color: var(--pearl) !important;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease), background .2s var(--ease); }
body .gradio-container span[data-testid=block-info] { margin-bottom: 8px; letter-spacing: .01em; }
body .gradio-container .block .wrap { border-radius: 14px; }
ul.options { z-index: 90 !important; background: #ffffff !important; border: 1px solid var(--line-2) !important;
  border-radius: 14px !important; box-shadow: 0 24px 60px -20px rgba(60,20,30,.24) !important; padding: 6px !important; }
ul.options li { border-radius: 10px; color: var(--pearl) !important; }
ul.options li:hover, ul.options li.active { background: rgba(138,21,56,.12) !important;
  color: var(--maroon) !important; }

/* segmented control */
body .gradio-container .seg .wrap { gap: 2px !important; display: inline-flex !important; width: auto !important; padding: 4px;
  border: 1px solid var(--line-2); border-radius: 999px; background: rgba(60,20,30,.04); }
body .gradio-container .seg label { border: 0 !important; background: none !important; padding: 6px 14px !important;
  border-radius: 999px !important; font-size: 13px !important; color: var(--pearl-2) !important; box-shadow: none !important;
  transition: background .3s var(--ease), color .3s var(--ease); cursor: pointer; }
body .gradio-container .seg label.selected { background: var(--accent-grad) !important; color: #fff !important; font-weight: 600;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.5), 0 6px 18px -8px rgba(138,21,56,.8) !important; }
body .gradio-container .seg label input { display: none !important; }
body .gradio-container .seg span[data-testid=block-info] { font-size: 12px; color: var(--muted); }
body .gradio-container .pills .wrap { gap: 8px !important; }
body .gradio-container .pills label { border-radius: 999px !important; padding: 8px 16px !important; font-size: 14px !important;
  box-shadow: none !important; transition: all .25s var(--ease); }
body .gradio-container .pills label.selected { box-shadow: 0 8px 22px -10px rgba(138,21,56,.9) !important; }
body .gradio-container .pills label input { display: none !important; }

/* accordion becomes a section with a serif title */
body .gradio-container .hs-section.block { background: none !important; border: 0 !important; padding: 0 !important; }
body .gradio-container .hs-section > .label-wrap { padding: 0 0 14px !important; border-bottom: 1px solid var(--line);
  margin-bottom: 22px; font-family: var(--serif) !important; font-size: 30px !important; font-weight: 400 !important;
  color: var(--pearl) !important; letter-spacing: -.01em; }

body .gradio-container .hs-section > .label-wrap span:first-child { font-family: var(--serif) !important; font-size: 30px !important;
  font-weight: 400 !important; color: var(--pearl) !important; }
body .gradio-container .hs-section > .label-wrap .icon { color: var(--maroon) !important; font-size: 11px !important; }
body .gradio-container .hs-section { overflow: visible !important; }

/* gradio columns styled as glass */
body .gradio-container .form-card, body .gradio-container .col-card { position: relative; isolation: isolate;
  background: var(--glass) !important; border: 1px solid var(--line) !important; border-radius: var(--r-lg) !important;
  padding: 22px !important; gap: 16px !important; backdrop-filter: blur(14px); box-shadow: var(--shadow);
  transition: border-color .4s var(--ease), transform .5s var(--spring), box-shadow .5s var(--ease); }
body .gradio-container .form-card.private { background: linear-gradient(180deg, #fbf0f2, #ffffff) !important;
  border: 1px dashed rgba(138,21,56,.28) !important; }
body .gradio-container .col-card { animation: hs-in .8s var(--ease) both; }
body .gradio-container .col-card:hover { border-color: rgba(138,21,56,.32) !important; transform: translateY(-4px);
  box-shadow: var(--shadow-hi), 0 0 0 4px rgba(214,160,70,.08); }
body .gradio-container .col-card:nth-child(2) { animation-delay: .08s; }
body .gradio-container .col-card:nth-child(3) { animation-delay: .16s; }
body .gradio-container .form-card::before, body .gradio-container .col-card::before { content: ""; position: absolute; inset: 0;
  border-radius: inherit; z-index: -1; pointer-events: none; opacity: 0; transition: opacity .4s var(--ease);
  background: radial-gradient(380px circle at var(--mx, 50%) var(--my, 0%), rgba(214,160,70,.16), transparent 60%); }
body .gradio-container .form-card:hover::before, body .gradio-container .col-card:hover::before { opacity: 1; }
body .gradio-container .col-card > .block:first-child { flex-grow: 1; }
body .gradio-container .col-card > button { flex-grow: 0 !important; }
body .gradio-container .sticky { position: sticky; top: 96px; align-self: flex-start; }
body .gradio-container .head-row { align-items: flex-end !important; justify-content: space-between; gap: 16px !important; }
body .gradio-container .head-row > :first-child { flex: 1 1 240px !important; min-width: 0 !important; }
body .gradio-container .head-row > :not(:first-child) { flex: 0 0 auto !important; width: auto !important; }
body .gradio-container .head-row > .form { background: none !important; }

/* toasts sit below the dock */
.toast-wrap { top: 84px !important; }
.toast-body { background: rgba(255,255,255,.96) !important; border: 1px solid rgba(138,21,56,.18) !important;
  border-radius: 18px !important; backdrop-filter: blur(16px);
  box-shadow: 0 24px 60px -20px rgba(60,20,30,.24), 0 0 0 4px rgba(214,160,70,.08) !important; }
.toast-body * { color: var(--pearl) !important; }
.toast-body .toast-icon, .toast-body .timer { display: none !important; }
.toast-title { font-size: 11px !important; text-transform: uppercase !important; letter-spacing: .12em; color: var(--gold) !important;
  font-weight: 600 !important; }
.toast-text { font-size: 14px !important; }
"""

# Our HTML components, scoped under "body .gradio-container" by _scope so they beat gradio's prose rules.
COMPONENT_CSS = """
.prose * { color: inherit; }
.prose { color: var(--pearl); }
.ic { width: 16px; height: 16px; flex-shrink: 0; stroke: currentColor; stroke-width: 1.6; fill: none;
  stroke-linecap: round; stroke-linejoin: round; vertical-align: -3px; }
.ic.sm { width: 14px; height: 14px; vertical-align: -2px; }
.ic.lg { width: 20px; height: 20px; }
.muted { color: var(--muted); }
.note { font-size: 13px; color: var(--muted); line-height: 1.55; margin: 0; }
.label { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 600; color: var(--gold);
  letter-spacing: .14em; text-transform: uppercase; margin: 0 0 10px; }
.num { font-variant-numeric: tabular-nums; }
.ar { font-family: var(--kufi); direction: rtl; unicode-bidi: isolate; }
.gold-text { background-image: var(--gold-text); background-size: 220% 100%; background-repeat: repeat; -webkit-background-clip: text; background-clip: text;
  color: transparent !important; animation: hs-shimmer 7s linear infinite; }
.serr { display: block; width: 64px; height: 9px; color: var(--gold); margin: 0 0 22px; overflow: visible; }
.serr path { fill: none; stroke: currentColor; stroke-width: 1.4; stroke-linejoin: round; stroke-linecap: round;
  stroke-dasharray: 120; stroke-dashoffset: 120; animation: hs-draw 1.4s var(--ease) .2s forwards; }
.rise { animation: hs-in .9s var(--ease) both; }
.rise.d1 { animation-delay: .08s; } .rise.d2 { animation-delay: .16s; } .rise.d3 { animation-delay: .24s; }
.rise.d4 { animation-delay: .32s; } .rise.d5 { animation-delay: .40s; }

/* ---------- header ---------- */
.top { display: flex; align-items: center; justify-content: space-between; gap: 16px; height: 76px; }
.logo { display: flex; align-items: center; gap: 12px; color: var(--pearl); }
.logo .mark { width: 32px; height: 32px; position: relative; flex-shrink: 0;
  filter: drop-shadow(0 4px 10px rgba(138,21,56,.25)); transition: transform .7s var(--spring); }
.logo:hover .mark { transform: rotate(-18deg) scale(1.06); }
.logo .mark svg { width: 32px; height: 32px; display: block; }
.logo .wm { font-family: var(--serif); font-size: 26px; letter-spacing: -.01em; line-height: 1; }
.logo .wm-ar { font-family: var(--kufi); font-size: 15px; color: var(--gold); padding-left: 12px; border-left: 1px solid var(--line-2);
  line-height: 1.1; }
.pdot { position: absolute; right: -2px; bottom: -2px; width: 9px; height: 9px; border-radius: 50%; background: var(--green);
  border: 2px solid var(--n1); }
.top .right { display: flex; align-items: center; gap: 14px; font-size: 13px; color: var(--muted); }
.top .place { display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; padding: 8px 14px; border-radius: 999px;
  border: 1px solid var(--line); background: rgba(255,255,255,.7); }
.top .place .ic { color: var(--gold); }
.account { display: flex; align-items: center; gap: 10px; padding: 4px 6px 4px 4px; border-radius: 999px;
  border: 1px solid var(--line-2); background: rgba(255,255,255,.8); backdrop-filter: blur(12px); box-shadow: var(--shadow); }
.account .nm { font-size: 13px; font-weight: 500; color: var(--pearl); }
.account .switch { font: inherit; font-size: 12px; font-weight: 600; color: var(--maroon); cursor: pointer; padding: 6px 12px;
  border-radius: 999px; background: rgba(138,21,56,.10); border: 1px solid rgba(138,21,56,.25);
  transition: background .25s var(--ease), color .25s; }
.account .switch:hover { background: var(--maroon); color: #fff; }

/* ---------- type ---------- */
.page-head { position: relative; isolation: isolate; margin: 8px 0 36px; min-height: 120px; display: flex; flex-direction: column; justify-content: flex-end; }
.page-head .art { position: absolute; right: -8px; top: -46px; z-index: -1; font-family: var(--ruqaa); font-weight: 700;
  font-size: clamp(96px, 15vw, 190px); line-height: 1.2; color: transparent; -webkit-text-stroke: 1px rgba(138,21,56,.16);
  pointer-events: none; white-space: nowrap; animation: hs-write 1.8s var(--ease) both; }
.page-head .greet-ar { display: table; align-self: flex-start; font-family: var(--ruqaa); font-size: 38px; line-height: 1.3; margin: 0 0 2px; }
.page-head h1 { font-family: var(--serif); font-weight: 400; font-size: 60px; line-height: 1; letter-spacing: -.02em; margin: 0;
  color: var(--pearl); }
.page-head h1 em { font-style: italic; }
.page-head p { margin: 14px 0 0; color: var(--muted); font-size: 15px; line-height: 1.55; max-width: 560px; }
h2.t { font-family: var(--serif); font-weight: 400; font-size: 30px; line-height: 1.1; letter-spacing: -.01em; margin: 0; color: var(--pearl); }
h3.t { font-size: 16px; line-height: 1.4; font-weight: 600; margin: 0; color: var(--pearl); }

/* ---------- avatars ---------- */
.av { width: 42px; height: 42px; border-radius: 50%; display: grid; place-items: center; flex-shrink: 0; position: relative;
  background: linear-gradient(140deg, #fbf1dc, #f6e3e8); color: var(--maroon);
  border: 1px solid rgba(138,21,56,.14); font-size: 13px; font-weight: 600; letter-spacing: .03em; }
.av.sm { width: 30px; height: 30px; font-size: 11px; }
.av.lg { width: 58px; height: 58px; font-size: 18px; }
.av.me { background: var(--accent-grad); color: #fff; border-color: transparent;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.3), 0 6px 18px -8px rgba(138,21,56,.6); }
.pair { display: flex; }
.pair .av { box-shadow: 0 0 0 3px #fff; }
.pair .av + .av { margin-left: -7px; }
.who { display: flex; align-items: center; gap: 12px; min-width: 0; }
.who .meta { min-width: 0; }
.who .nm { font-size: 15px; font-weight: 600; letter-spacing: -.01em; color: var(--pearl); display: block; }
.who .sub { font-size: 13px; color: var(--muted); display: block; margin-top: 2px; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; }

/* ---------- tags, dots, status ---------- */
.tag { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; line-height: 1;
  padding: 6px 10px; border-radius: 999px; background: rgba(60,20,30,.05); border: 1px solid var(--line);
  color: var(--pearl-2); white-space: nowrap; }
.tag.good { background: rgba(35,130,76,.10); border-color: rgba(35,130,76,.25); color: var(--green); }
.tag.warn { background: rgba(168,109,18,.10); border-color: rgba(168,109,18,.28); color: var(--amber); }
.tag.maroon { background: rgba(196,42,90,.18); border-color: rgba(138,21,56,.25); color: var(--rose); }
.tag.gold { background: #fbf1dc; border-color: rgba(214,160,70,.4); color: var(--gold); }
.tags { display: flex; gap: 6px; flex-wrap: wrap; }
.dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; display: inline-block; flex-shrink: 0; }
.dot.live { background: var(--green); box-shadow: 0 0 10px var(--green); animation: hs-live 2s ease-out infinite; }
.status { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--pearl-2); margin: 16px 0 0; line-height: 1.45; }
.status .dot { color: var(--faint); }
.status.ok .dot { color: var(--green); box-shadow: 0 0 10px var(--green); }
.status.warn .dot { color: var(--amber); }
.status.busy .dot { color: var(--maroon); box-shadow: 0 0 10px rgba(138,21,56,.5); animation: hs-breathe 1.4s ease-in-out infinite; }
.status.busy span { background: linear-gradient(90deg, var(--pearl-2) 0%, var(--maroon-hi) 45%, var(--pearl-2) 70%);
  background-size: 250% 100%; -webkit-background-clip: text; background-clip: text; color: transparent !important;
  animation: hs-shimmer 2.4s linear infinite; }
.loading { display: inline-flex; align-items: center; gap: 10px; font-size: 13px; color: var(--pearl-2); }
.spin { width: 15px; height: 15px; border-radius: 50%; flex-shrink: 0;
  background: conic-gradient(from 0deg, transparent 0 25%, var(--gold) 100%);
  -webkit-mask: radial-gradient(circle, transparent 55%, #000 57%); mask: radial-gradient(circle, transparent 55%, #000 57%);
  animation: hs-spin .9s linear infinite; }
.typing { display: inline-flex; gap: 4px; align-items: center; height: 14px; color: inherit; }
.typing i { width: 5px; height: 5px; border-radius: 50%; background: currentColor; opacity: .35; animation: hs-typing 1.2s infinite ease-in-out; }
.typing i:nth-child(2) { animation-delay: .15s; } .typing i:nth-child(3) { animation-delay: .3s; }

/* ---------- glass surfaces with a cursor spotlight ---------- */
.card, .person, .search, .chat, .verdict, .next, .rows, .batch-list, .vault, .stat-row {
  position: relative; isolation: isolate; background: var(--glass); border: 1px solid var(--line);
  border-radius: var(--r-lg); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); box-shadow: var(--shadow);
  transition: border-color .4s var(--ease), transform .5s var(--spring), box-shadow .5s var(--ease); }
.card::before, .person::before, .search::before, .verdict::before, .next::before, .rows::before, .batch-list::before,
.vault::before { content: ""; position: absolute; inset: 0; border-radius: inherit; z-index: -1; pointer-events: none; opacity: 0;
  background: radial-gradient(420px circle at var(--mx, 50%) var(--my, 0%), rgba(214,160,70,.16), transparent 60%);
  transition: opacity .4s var(--ease); }
.card:hover::before, .person:hover::before, .search:hover::before, .verdict:hover::before, .next:hover::before,
.rows:hover::before, .batch-list:hover::before, .vault:hover::before { opacity: 1; }
.card { padding: 22px; }
.card + .card { margin-top: 14px; }
.lift { cursor: pointer; }
.lift:hover { border-color: rgba(138,21,56,.3); }
.empty { text-align: center; padding: 64px 24px; border: 1px dashed var(--line-2); border-radius: var(--r-lg);
  background: rgba(255,255,255,.6); }
.empty .ico { width: 54px; height: 54px; border-radius: 50%; display: grid; place-items: center; margin: 0 auto 16px;
  background: #fbf1dc; color: var(--maroon); border: 1px solid rgba(214,160,70,.4);
  box-shadow: 0 10px 30px -12px rgba(214,160,70,.6); }
.empty .ico .ic { width: 22px; height: 22px; }
.empty h3 { font-family: var(--serif); font-weight: 400; font-size: 26px; margin: 0 0 6px; color: var(--pearl); }
.empty p { margin: 0; font-size: 14px; color: var(--muted); }

.hbtn { position: relative; overflow: hidden; isolation: isolate; display: inline-flex; align-items: center; gap: 8px; font: inherit;
  font-size: 14px; font-weight: 600; border-radius: 999px; padding: 10px 20px; min-height: 42px; cursor: pointer;
  border: 1px solid var(--line-2); background: rgba(60,20,30,.05); color: var(--pearl); white-space: nowrap;
  transition: transform .25s var(--spring), border-color .3s var(--ease), box-shadow .3s var(--ease), background .3s, color .3s; }
.hbtn:hover { border-color: rgba(138,21,56,.55); color: var(--maroon); transform: translateY(-1px);
  box-shadow: 0 0 0 4px rgba(138,21,56,.08), 0 10px 30px -14px rgba(138,21,56,.6); }
.hbtn:active { transform: scale(.97); }
.hbtn.primary { background: var(--accent-grad); border-color: transparent; color: #fff;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.28), inset 0 -2px 0 rgba(60,5,20,.25), 0 12px 28px -12px rgba(138,21,56,.55); }
.hbtn.primary::after { content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none;
  background: linear-gradient(105deg, transparent 30%, rgba(255,236,190,.38) 48%, transparent 66%);
  transform: translateX(-130%); animation: hs-sweep 4.5s var(--ease) infinite 1s; }
.hbtn.primary:hover { color: #fff; transform: translateY(-2px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.28), 0 18px 40px -12px rgba(138,21,56,.65); }
.hbtn.ghost { border-color: transparent; background: none; color: var(--muted); }
.hbtn.ghost:hover { color: var(--pearl); background: rgba(60,20,30,.05); box-shadow: none; }
.hbtn.link { border-color: transparent; background: none; padding-left: 6px; padding-right: 6px; color: var(--pearl-2); }
.hbtn.link:hover { color: var(--maroon); box-shadow: none; }
.hbtn .ic { transition: transform .35s var(--spring); }
.hbtn:hover .ic.arrow { transform: translateX(4px); }
.actions { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: 18px; }
:focus-visible { outline: 2px solid var(--gold); outline-offset: 3px; }

/* ---------- landing ---------- */
.hero { position: relative; isolation: isolate; padding: 56px 0 28px; min-height: 400px; }
.hero .callig { position: absolute; right: -10px; top: -30px; z-index: -1; font-family: var(--ruqaa); font-weight: 700;
  font-size: clamp(130px, 21vw, 270px); line-height: 1.3; pointer-events: none; white-space: nowrap;
  animation: hs-write 2.4s var(--ease) .15s both; }
.hero .callig .gold-text { animation-duration: 9s; }
.hero .khatam { position: absolute; right: 120px; top: -60px; width: 440px; height: 440px; z-index: -2; color: var(--gold);
  color: var(--gold-orn); opacity: .35; animation: hs-turn 90s linear infinite; pointer-events: none; }
.hero .kicker { display: inline-flex; align-items: center; gap: 10px; font-size: 12px; font-weight: 500; color: var(--pearl-2);
  padding: 7px 14px 7px 10px; border-radius: 999px; border: 1px solid var(--line-2); background: rgba(255,255,255,.75);
  backdrop-filter: blur(10px); margin: 0 0 28px; box-shadow: var(--shadow); }
.hero h1 { font-family: var(--serif); font-weight: 400; font-size: clamp(52px, 8vw, 96px); line-height: .96; letter-spacing: -.025em;
  margin: 0; color: var(--pearl); max-width: 820px; }
.hero h1 em { font-style: italic; }
.hero .h1-ar { display: table; font-family: var(--kufi); font-size: 22px; color: var(--gold); margin: 22px 0 0; line-height: 1.6; }
.hero .lede { font-size: 18px; line-height: 1.5; color: var(--muted); margin: 24px 0 0; max-width: 480px; }
.section-label { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin: 72px 0 16px; }
.section-label h2 { font-family: var(--serif); font-weight: 400; font-size: 28px; line-height: 1; margin: 0; color: var(--pearl); }
.section-label h2 em { font-style: italic; }
.section-label p { margin: 0; font-size: 13px; color: var(--muted); max-width: 320px; text-align: right; }
.people { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.person { display: flex; flex-direction: row; align-items: center; justify-content: space-between; gap: 12px; text-align: left; padding: 16px 18px; cursor: pointer;
  animation: hs-in .9s var(--ease) both; }
.person:nth-child(2) { animation-delay: .08s; } .person:nth-child(3) { animation-delay: .16s; }
.person:hover { border-color: rgba(138,21,56,.4); transform: translateY(-6px);
  box-shadow: var(--shadow-hi), 0 0 0 4px rgba(214,160,70,.08); }
.person:active { transform: translateY(-2px) scale(.99); }
.person .role { font-family: var(--kufi); font-size: 12px; color: var(--gold); }
.person p { margin: 0; font-size: 14px; line-height: 1.6; color: var(--pearl-2); flex-grow: 1; }
.person .go { display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
  color: var(--maroon); background: rgba(138,21,56,.06); transition: background .3s var(--ease), color .3s var(--ease); }
.person:hover .go { background: var(--maroon); color: #fff; }
.person .go .ic { transition: transform .35s var(--spring); }
.person:hover .go .ic { transform: translateX(5px); }
.how { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.how > div { padding: 22px; border-radius: var(--r-lg); border: 1px solid var(--line); background: rgba(255,255,255,.6); }
.how .n { font-family: var(--serif); font-style: italic; font-size: 40px; line-height: 1; }
.how h3 { font-size: 16px; font-weight: 600; margin: 14px 0 6px; color: var(--pearl); }
.how p { font-size: 14px; line-height: 1.6; color: var(--muted); margin: 0; }
.figures { display: flex; gap: 40px; flex-wrap: wrap; margin-top: 40px; padding-top: 28px; border-top: 1px solid var(--line); }
.figures span { font-size: 13px; color: var(--muted); display: flex; flex-direction: column; gap: 4px; }
.figures b { font-family: var(--serif); font-weight: 400; font-size: 52px; line-height: 1; color: var(--pearl); }

/* three-step flow: equal columns, gold icon tiles, a dashed gold thread between them */
.flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; margin: 56px 0 0; padding: 30px 32px 32px;
  border-radius: var(--r-lg); background: var(--glass); border: 1px solid rgba(214,160,70,.24); box-shadow: var(--shadow); }
.fstep { position: relative; display: flex; flex-direction: column; align-items: flex-start; gap: 0; }
.fstep:not(:last-child)::after { content: ""; position: absolute; top: 28px; left: 76px; right: -20px; height: 1px;
  background: repeating-linear-gradient(90deg, var(--gold-orn) 0 5px, transparent 5px 10px); opacity: .7; }
.fstep:not(:last-child)::before { content: ""; position: absolute; top: 25px; right: -24px; width: 7px; height: 7px;
  background: var(--gold-orn); transform: rotate(45deg); border-radius: 1px; }
.ftile { position: relative; width: 56px; height: 56px; border-radius: 18px; display: grid; place-items: center; overflow: hidden;
  background: linear-gradient(145deg, #fffaf0, #f7e6c2); border: 1px solid rgba(201,154,69,.45); color: var(--maroon);
  box-shadow: inset 0 1px 0 #fff, 0 10px 24px -14px rgba(176,122,42,.8);
  transition: transform .5s var(--spring), box-shadow .4s var(--ease); }
.ftile .ic { width: 24px; height: 24px; stroke-width: 1.5; }
.ftile::after { content: ""; position: absolute; inset: 0; width: 45%;
  background: linear-gradient(105deg, transparent, rgba(255,255,255,.85), transparent); transform: translateX(-160%);
  animation: hs-tile 5s var(--ease) infinite; }
.fstep:nth-child(2) .ftile::after { animation-delay: .5s; } .fstep:nth-child(3) .ftile::after { animation-delay: 1s; }
.fstep:hover .ftile { transform: translateY(-3px) rotate(-4deg); box-shadow: inset 0 1px 0 #fff, 0 16px 30px -14px rgba(176,122,42,.9); }
.fbadge { position: absolute; left: 42px; top: -6px; z-index: 2; width: 22px; height: 22px; border-radius: 50%;
  display: grid; place-items: center; background: var(--accent-grad); color: #fff !important; font-family: var(--kufi);
  font-size: 12px; font-weight: 600; box-shadow: 0 0 0 3px #fff, 0 4px 10px -4px rgba(138,21,56,.7); }
.fstep b { display: block; margin-top: 18px; font-family: var(--serif); font-weight: 400; font-size: 24px; line-height: 1.1;
  color: var(--pearl); letter-spacing: -.01em; }
.fstep .fd { display: block; margin-top: 6px; font-size: 13px; line-height: 1.5; color: var(--muted); }

/* ---------- home ---------- */
/* the one dark moment on the page: what needs you next */
.next { display: flex; align-items: center; justify-content: space-between; gap: 24px; flex-wrap: wrap; padding: 30px 32px;
  overflow: hidden; border: 0; color: #fff;
  background: radial-gradient(120% 140% at 100% 0%, #b72a55 0%, #8a1538 45%, #5e0c25 100%);
  box-shadow: 0 2px 4px rgba(60,20,30,.06), 0 30px 60px -30px rgba(110,15,43,.65); }
.next::before { display: none; }
.next .khatam { position: absolute; right: -40px; top: -90px; width: 300px; height: 300px; z-index: -1; color: var(--gold-hi);
  opacity: .22; animation: hs-turn 120s linear infinite; pointer-events: none; }
.next .label { color: var(--gold-hi); margin-bottom: 10px; }
.next h2.t { color: #fff; font-size: 34px; }
.next p { margin: 10px 0 0; font-size: 14px; color: rgba(255,255,255,.72); }
.next .hbtn.primary { background: var(--gold-grad); color: #2a1408; border-color: transparent;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.6), 0 12px 28px -12px rgba(0,0,0,.45); }
.next .hbtn.primary:hover { color: #2a1408; }
.next.calm { background: var(--glass); color: var(--pearl); border: 1px solid var(--line); box-shadow: var(--shadow); }
.next.calm .label { color: var(--gold); } .next.calm h2.t { color: var(--pearl); } .next.calm p { color: var(--muted); }
.next.calm .khatam { color: var(--gold-orn); opacity: .18; }
/* one quiet strip of numbers */
.stats { display: grid; grid-template-columns: repeat(4, 1fr); margin: 16px 0; border-radius: var(--r-lg);
  background: var(--glass); border: 1px solid var(--line); box-shadow: var(--shadow); }
.stat { padding: 20px 24px; border-left: 1px solid var(--line); }
.stat:first-child { border-left: 0; }
.stat b { display: block; font-family: var(--serif); font-weight: 400; font-size: 44px; line-height: 1; color: var(--pearl);
  font-variant-numeric: tabular-nums; }
.stat span { display: block; margin-top: 6px; font-size: 12px; color: var(--muted); }
.stat.hot b { color: var(--maroon); }
.dash { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr); gap: 16px; align-items: stretch; }
.dash > .card { display: flex; flex-direction: column; margin-top: 0; }
.empty-feed { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px;
  text-align: center; color: var(--muted); font-size: 14px; padding: 32px 0; }
.empty-feed .ico { width: 48px; height: 48px; border-radius: 50%; display: grid; place-items: center; background: #fbf1dc;
  color: var(--gold); border: 1px solid rgba(214,160,70,.35); }
.agent .status-line { display: inline-flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 600; color: var(--green);
  margin-bottom: 18px; letter-spacing: .12em; text-transform: uppercase; }
.agent .who .sub, .agent-grid .who .sub { white-space: normal; }
.agent .looking { margin: 18px 0 0; font-size: 14px; line-height: 1.6; color: var(--pearl-2); }
.limits { list-style: none; margin: 18px 0 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.limits li { display: flex; gap: 10px; align-items: flex-start; padding: 11px 14px; border-radius: 14px; font-size: 14px; line-height: 1.45;
  color: var(--pearl); background: rgba(138,21,56,.045); border: 1px solid rgba(138,21,56,.10); }
.limits li .ic { color: var(--maroon); margin-top: 2px; }
.limits li.none { color: var(--muted); background: rgba(60,20,30,.03); border-color: var(--line); }
.feed { list-style: none; margin: 0; padding: 0; }
.ev { display: grid; grid-template-columns: 34px 1fr auto; gap: 12px; align-items: center; padding: 12px 0;
  border-top: 1px solid var(--line); font-size: 14px; color: var(--pearl); }
.ev:first-child { border-top: 0; padding-top: 0; }
.ev .i { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; background: #fbf1dc;
  color: var(--gold); border: 1px solid rgba(214,160,70,.35); }
.ev .i.good { background: rgba(35,130,76,.10); color: var(--green); border-color: rgba(35,130,76,.25); }
.ev .tm { font-size: 12px; color: var(--faint); white-space: nowrap; }
.ev b { font-weight: 600; color: var(--maroon); }

/* ---------- matches: the live search ---------- */
.search { padding: 20px 24px; }
.search .head { display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 600; color: var(--pearl); margin-bottom: 10px; }
.sstep { display: grid; grid-template-columns: 24px 1fr auto; gap: 14px; align-items: start; padding: 12px 0; border-top: 1px solid var(--line); }
.sstep:first-of-type { border-top: 0; }
.sstep .ic-wrap { width: 20px; height: 20px; margin-top: 1px; border-radius: 50%; border: 1.5px solid var(--line-2);
  display: grid; place-items: center; color: #fff; }
.sstep .ic-wrap .ic { width: 12px; height: 12px; stroke-width: 2.6; }
.sstep.done .ic-wrap { background: var(--accent-grad); border-color: transparent; box-shadow: 0 4px 12px -4px rgba(138,21,56,.5); }
.sstep.now .ic-wrap { border-color: var(--maroon); box-shadow: 0 0 0 0 rgba(138,21,56,.5); animation: hs-ripple 1.6s ease-out infinite; }
.sstep.now .ic-wrap::after { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--maroon); }
.sstep .t { font-size: 14px; font-weight: 500; color: var(--pearl); }
.sstep .d { color: var(--muted); font-size: 13px; margin-top: 6px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.sstep .n { font-size: 12px; color: var(--muted); white-space: nowrap; font-variant-numeric: tabular-nums; }
.sstep .n .minus { color: var(--rose); margin-right: 6px; }
.cands { margin-top: 12px; display: flex; flex-direction: column; gap: 6px; }
.cand { display: grid; grid-template-columns: 30px minmax(120px, 1.2fr) 90px minmax(150px, 1.5fr); gap: 12px; align-items: center;
  padding: 10px 12px; border-radius: 14px; background: rgba(60,20,30,.03); border: 1px solid transparent;
  transition: opacity .4s var(--ease), border-color .4s; }
.cand .nm { font-weight: 600; font-size: 13px; color: var(--pearl); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cand .hl { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cand .bar { height: 4px; border-radius: 4px; background: rgba(60,20,30,.08); overflow: hidden; }
.cand .bar i { display: block; height: 100%; border-radius: 4px; background: var(--pearl-2); transform-origin: left;
  animation: hs-grow 1s var(--ease) both; }
.cand.strong { border-color: rgba(138,21,56,.28); background: rgba(138,21,56,.06); }
.cand.strong .bar i { background: linear-gradient(90deg, var(--gold-orn), var(--maroon)); }
.cand .vd { font-size: 12px; display: flex; flex-direction: column; gap: 5px; align-items: flex-start; }
.cand .vd .why { color: var(--muted); line-height: 1.45; }
.cand.weak { opacity: .4; }
details.search > summary { cursor: pointer; list-style: none; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
details.search > summary::-webkit-details-marker { display: none; }
details.search > summary .more { margin-left: auto; font-size: 13px; color: var(--maroon); display: inline-flex; align-items: center; gap: 4px; }
details.search > summary .more .ic { transition: transform .4s var(--spring); }
details.search[open] > summary .more .ic { transform: rotate(180deg); }
details.search[open] > summary { margin-bottom: 12px; }
.funnel { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 14px; color: var(--muted); }
.funnel b { font-family: var(--serif); font-weight: 400; font-size: 24px; color: var(--pearl); margin-right: 4px; vertical-align: -2px; }
.funnel > span:last-child b { color: var(--maroon); }
.funnel .arr { color: var(--gold); opacity: .6; }
.funnel > .ic { color: var(--gold); }

/* match card */
.match .top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; height: auto; }
.match .head-line { font-size: 14px; line-height: 1.55; color: var(--pearl-2); margin: 16px 0 0; }
.match .why { margin: 16px 0 0; padding: 14px 0 0; border-top: 1px solid var(--line); font-size: 14px; line-height: 1.6; color: var(--pearl-2); }
.match .tags { margin-top: 14px; }

/* score ring that draws itself */
.score { position: relative; width: 64px; height: 64px; flex-shrink: 0; display: grid; place-items: center; }
.score svg { position: absolute; inset: 0; width: 100%; height: 100%; transform: rotate(-90deg); overflow: visible; }
.score circle { fill: none; stroke-width: 2.5; stroke-linecap: round; }
.score .bg { stroke: rgba(60,20,30,.08); }
.score .fg { stroke: url(#hs-gold); stroke-dasharray: 100;
  animation: hs-ring 1.4s var(--ease) both .2s; }
.score b { font-family: var(--serif); font-weight: 400; font-size: 26px; line-height: 1; color: var(--pearl); margin-top: -4px; }
.score span { position: absolute; bottom: 9px; font-size: 9px; letter-spacing: .14em; text-transform: uppercase; color: var(--gold); }
.score.xl { width: 120px; height: 120px; }
.score.xl b { font-size: 50px; margin-top: -8px; }
.score.xl span { bottom: 20px; font-size: 10px; }
.score.xl circle { stroke-width: 2; }

/* ---------- conversation ---------- */
.room { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; padding: 0 0 20px;
  margin-bottom: 22px; border-bottom: 1px solid var(--line); }
.room .names { font-family: var(--serif); font-size: 30px; line-height: 1.05; color: var(--pearl); letter-spacing: -.01em; }
.room .names span { font-style: italic; color: var(--gold); margin: 0 8px; }
.room .sub { font-size: 13px; color: var(--muted); margin-top: 6px; }
.room .tags { margin-top: 4px; }
.stepper { display: flex; align-items: center; gap: 10px; margin: 0 0 16px; }
.stepper .st { display: flex; align-items: center; gap: 7px; font-size: 12px; color: var(--faint); white-space: nowrap; }
.stepper .st i { width: 8px; height: 8px; border-radius: 50%; background: var(--line-2); }
.stepper .st.done { color: var(--pearl-2); } .stepper .st.done i { background: var(--maroon); }
.stepper .st.now { color: var(--maroon); font-weight: 600; }
.stepper .st.now i { background: var(--maroon); animation: hs-ripple 1.6s ease-out infinite; }
.stepper .line { flex: 1; height: 1px; background: var(--line-2); min-width: 10px; }
.stepper .line.done { background: linear-gradient(90deg, var(--maroon), var(--gold-orn)); }
.chat { display: flex; flex-direction: column; gap: 18px; min-height: 240px; max-height: min(560px, 68vh); overflow-y: auto;
  overscroll-behavior: contain; scroll-behavior: smooth; padding: 22px; background: linear-gradient(180deg, #fdfaf5, #f8f2ea);
  scrollbar-width: thin; scrollbar-color: rgba(138,21,56,.25) transparent; }
.chat::-webkit-scrollbar { width: 6px; } .chat::-webkit-scrollbar-thumb { background: rgba(138,21,56,.22); border-radius: 6px; }
.chat .msg { flex-shrink: 0; }
.msg { display: flex; gap: 10px; align-items: flex-end; max-width: 86%; }
.msg.me { align-self: flex-end; flex-direction: row-reverse; }
.bubble { padding: 12px 16px; border-radius: 20px; line-height: 1.6; font-size: 14px; }
.bubble .who-l { font-size: 10px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; opacity: .65; margin-bottom: 4px; }
.msg.them .bubble { background: #fff; box-shadow: var(--shadow); border: 1px solid var(--line); border-bottom-left-radius: 6px; color: var(--pearl); }
.msg.me .bubble { background: linear-gradient(140deg, #b0234f, #7a1232 60%, #5e0d26); color: #fff; border-bottom-right-radius: 6px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.18), 0 14px 30px -14px rgba(138,21,56,.55); }
.msg.me .bubble * { color: inherit; }
.shield { display: inline-flex; align-items: center; gap: 5px; margin-top: 8px; font-size: 11px; color: var(--green); font-weight: 500; }
.msg.me .shield { color: var(--gold-hi); }
.chat .waiting { margin: auto; padding: 40px 0; }
.vault { padding: 22px; background: linear-gradient(170deg, #fbeff2, #ffffff 70%); border: 1px dashed rgba(138,21,56,.26); }
.vault h4 { margin: 0; display: flex; align-items: center; gap: 10px; font-family: var(--serif); font-weight: 400; font-size: 24px; color: var(--pearl); }
.vault h4 .ic { color: var(--maroon); width: 20px; height: 20px; }
.vault .note { margin-top: 6px; }
.vault .meter { font-size: 12px; color: var(--muted); margin-top: 14px; display: flex; gap: 8px 14px; flex-wrap: wrap; }
.vault .meter span { display: inline-flex; align-items: center; gap: 6px; }
.vault .meter .ok { color: var(--green); }
.vault .thinking { margin-top: 14px; }
.vault .notes { margin: 0; padding: 0; list-style: none; }
.vault .notes li { font-size: 13px; color: var(--pearl-2); padding: 10px 0; border-top: 1px solid var(--line); line-height: 1.55; font-style: italic; }
.vault .label { margin-top: 20px; }
.their-banner { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; font-size: 13px; color: var(--pearl-2);
  background: #fbf3e3; border: 1px solid rgba(138,21,56,.25); border-radius: 999px; padding: 8px 8px 8px 18px; margin-bottom: 22px; }
.their-banner .ic { color: var(--gold); }
.their-banner .hbtn { margin-left: auto; min-height: 34px; padding: 6px 14px; font-size: 13px; }

/* conversation list */
.clist { display: flex; flex-direction: column; gap: 4px; }
.clist .label { margin: 0 12px 10px; }
.crow { display: flex; gap: 12px; align-items: center; padding: 12px; border-radius: 18px; cursor: pointer; border: 1px solid transparent;
  transition: background .3s var(--ease), border-color .3s var(--ease), transform .4s var(--spring); }
.crow:hover { background: rgba(60,20,30,.04); transform: translateX(3px); }
.crow.sel { background: linear-gradient(110deg, #f9ebef, #ffffff); border-color: rgba(138,21,56,.18); box-shadow: var(--shadow); }
.crow .meta { flex: 1; min-width: 0; }
.crow .meta b { font-size: 14px; font-weight: 600; display: block; color: var(--pearl); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.crow .h { font-size: 12px; color: var(--muted); display: flex; gap: 6px; align-items: center; margin-top: 3px; }
.crow .score-s { font-family: var(--serif); font-size: 24px; color: var(--maroon); }
.crow.live { cursor: default; }
.crow.live .h { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.live-pill { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: var(--green);
  letter-spacing: .1em; text-transform: uppercase; }

/* verdict */
.verdict { overflow: hidden; animation: hs-in .9s var(--ease) both; }
.verdict-head { position: relative; isolation: isolate; display: flex; justify-content: space-between; align-items: center; gap: 24px; padding: 28px 28px 24px; overflow: hidden; }
.verdict-head .art { position: absolute; left: 40%; top: -20px; font-family: var(--ruqaa); font-weight: 700; font-size: 120px; line-height: 1.2;
  color: transparent; -webkit-text-stroke: 1px rgba(138,21,56,.18); pointer-events: none; z-index: -1; white-space: nowrap; }
.verdict-head h2 { display: flex; align-items: center; gap: 14px; font-family: var(--serif); font-weight: 400; font-style: italic;
  font-size: 48px; line-height: 1; letter-spacing: -.02em; margin: 4px 0 12px; color: var(--pearl); }
.verdict-head h2 .dot { width: 12px; height: 12px; }
.verdict.worth_meeting .verdict-head h2 .dot { color: var(--green); box-shadow: 0 0 16px var(--green); }
.verdict.maybe_later .verdict-head h2 .dot { color: var(--amber); box-shadow: 0 0 16px var(--amber); }
.verdict.not_fit .verdict-head h2 .dot { color: var(--faint); }
.verdict.worth_meeting { border-color: rgba(35,130,76,.22); }
.verdict-head .note { max-width: 520px; }
.verdict-grid { display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid var(--line); }
.verdict-grid section { padding: 20px 28px 22px; border-bottom: 1px solid var(--line); }
.verdict-grid section:nth-child(odd) { border-right: 1px solid var(--line); }
.verdict-grid h4 { display: flex; align-items: center; gap: 8px; margin: 0 0 10px; font-size: 11px; font-weight: 600; color: var(--gold);
  letter-spacing: .14em; text-transform: uppercase; }
.verdict-grid ul { padding-left: 18px; margin: 0; }
.verdict-grid li { margin-bottom: 8px; line-height: 1.55; font-size: 14px; color: var(--pearl-2); }
.verdict-grid li::marker { color: var(--gold); }
.letter { padding: 22px 28px 24px; background: #fcf8f1; }
.intro { white-space: pre-wrap; font-family: var(--serif); font-size: 21px; line-height: 1.5; color: var(--pearl); margin: 10px 0 14px;
  padding-left: 18px; border-left: 2px solid var(--gold); }
.placeholder { color: var(--muted); list-style: none; margin-left: -18px; }
[dir=rtl] .intro, .intro[dir=rtl] { padding-left: 0; padding-right: 18px; border-left: 0; border-right: 2px solid var(--gold); font-family: var(--kufi); font-size: 18px; }
[dir=rtl] .verdict-grid section:nth-child(odd) { border-right: 0; border-left: 1px solid var(--line); }
[dir=rtl] .verdict-grid ul { padding-left: 0; padding-right: 18px; }
[dir=rtl] .verdict-head h2 { font-family: var(--ruqaa); font-style: normal; }
[dir=rtl] { font-family: var(--kufi); }
.decision { display: flex; gap: 12px; align-items: flex-start; margin-top: 16px; padding: 16px 18px; border-radius: 18px;
  background: rgba(60,20,30,.04); border: 1px solid var(--line); font-size: 14px; color: var(--pearl-2); line-height: 1.55; }
.decision b { color: var(--pearl); font-weight: 600; }
.decision .ic { margin-top: 2px; color: var(--gold); }
.decision.done { background: rgba(35,130,76,.08); border-color: rgba(35,130,76,.28); } .decision.done .ic { color: var(--green); }
.decision.wait .typing { color: var(--amber); margin-top: 6px; }
.msgnote { margin-top: 12px; font-size: 14px; background: #fff; border-radius: 14px; padding: 12px 14px;
  border: 1px solid var(--line); color: var(--pearl); }
.msgnote .label { margin-bottom: 4px; }

/* batch */
.batch-summary h3 { font-family: var(--serif); font-weight: 400; font-size: 30px; line-height: 1.15; margin: 4px 0 0; color: var(--pearl); }
.batch-summary .meter { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
.batch-list { display: flex; flex-direction: column; margin-top: 16px; }
.batch-row { display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap; padding: 16px 22px;
  border-top: 1px solid var(--line); transition: background .3s var(--ease); }
.batch-row:first-child { border-top: 0; }
.batch-row.lift:hover { background: rgba(138,21,56,.05); }
.batch-state { display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--pearl-2); }
.batch-state .go { display: inline-flex; color: var(--gold); transition: transform .35s var(--spring); }
.batch-row.lift:hover .go { transform: translateX(4px); }
.verdict-mini { display: flex; align-items: center; gap: 12px; }
.verdict-mini b { font-family: var(--serif); font-weight: 400; font-size: 26px; color: var(--maroon); }

/* intros */
.group { margin-top: 34px; }
.group:first-child { margin-top: 0; }
.group > h4, .group > summary h4 { display: flex; align-items: center; gap: 10px; margin: 0 0 14px; font-size: 11px; font-weight: 600;
  color: var(--gold); letter-spacing: .14em; text-transform: uppercase; }
.group h4 .count { font-size: 11px; color: #fff; background: var(--accent-grad); border-radius: 999px; padding: 2px 8px; letter-spacing: 0; }
.intro-card .top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.intro-card .why-line { color: var(--pearl); font-family: var(--serif); font-size: 22px; line-height: 1.35; margin: 18px 0 0; }
.intro-card .meta-line { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 14px; font-size: 13px; color: var(--muted); }
.intro-card.connected { border-color: rgba(35,130,76,.3); background: linear-gradient(170deg, rgba(35,130,76,.08), rgba(60,20,30,.02)); }
.wait-pill { display: inline-flex; align-items: center; gap: 8px; color: var(--amber); font-size: 13px; white-space: nowrap; }
.mini { display: flex; gap: 12px; align-items: center; padding: 14px 18px; border-top: 1px solid var(--line); cursor: pointer;
  transition: background .3s var(--ease); }
.mini:first-child { border-top: 0; }
.mini:hover { background: rgba(138,21,56,.05); }
.mini .meta { flex: 1; min-width: 0; }
.mini .meta b { font-size: 14px; font-weight: 600; color: var(--pearl); }
.mini .h { font-size: 13px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mini .go { color: var(--gold); display: inline-flex; transition: transform .35s var(--spring); }
.mini:hover .go { transform: translateX(4px); }
.mini.static { cursor: default; }
details.fold > summary { list-style: none; cursor: pointer; }
details.fold > summary::-webkit-details-marker { display: none; }
details.fold > summary h4 .ic { transition: transform .4s var(--spring); }
details.fold[open] > summary h4 .ic { transform: rotate(180deg); }
details.fold .note { margin: 0 0 12px; }

/* my agent */
.agent-grid { display: grid; grid-template-columns: 1.35fr 1fr; gap: 16px; margin-bottom: 56px; align-items: start; }
.agent-grid .bio { font-size: 14px; line-height: 1.65; color: var(--pearl-2); margin: 18px 0 0; }
.terms { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin-top: 18px; }
.term { padding: 12px 14px; border-radius: 14px; background: rgba(60,20,30,.04); border: 1px solid var(--line); font-size: 14px; color: var(--pearl); }
.term span { display: block; color: var(--gold); font-size: 10px; letter-spacing: .14em; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
.form-head h3 { font-family: var(--serif); font-weight: 400; font-size: 26px; margin: 0; display: flex; align-items: center; gap: 10px; color: var(--pearl); }
.form-head h3 .ic { color: var(--gold); width: 20px; height: 20px; }
.form-head p { margin: 6px 0 0; font-size: 13px; color: var(--muted); }
.form-intro { font-size: 15px; color: var(--pearl-2); line-height: 1.65; margin: 0 0 18px; max-width: 640px; }

@media (max-width: 900px) {
  .hero { min-height: 0; padding-top: 8px; }
  .hero .callig { position: relative; display: block; right: auto; top: auto; font-size: 110px; text-align: right; margin: -10px 0 -20px; }
  .hero .khatam { right: -80px; top: -40px; width: 300px; height: 300px; }
  .people, .how, .dash, .agent-grid { grid-template-columns: 1fr; }
  .flow { grid-template-columns: 1fr; gap: 26px; padding: 24px; }
  .fstep:not(:last-child)::after, .fstep:not(:last-child)::before { display: none; }
  .stats { grid-template-columns: repeat(2, 1fr); }
  .verdict-grid { grid-template-columns: 1fr; }
  .verdict-grid section:nth-child(odd) { border-right: 0; }
  .verdict-head { flex-direction: column-reverse; align-items: flex-start; }
  .cand { grid-template-columns: 30px 1fr; } .cand .bar, .cand .hl { display: none; } .cand .vd { grid-column: 1 / -1; }
  .msg { max-width: 96%; }
  .stepper .st span { display: none; }
  .top .place, .logo .wm-ar { display: none; }
  .account .nm { display: none; }
  .page-head h1 { font-size: 44px; }
  .section-label { flex-direction: column; align-items: flex-start; } .section-label p { text-align: left; }
}
"""

KEYFRAMES = """
@keyframes hs-in { from { opacity: 0; transform: translateY(18px); filter: blur(8px); } to { opacity: 1; transform: none; filter: none; } }
@keyframes hs-write { from { clip-path: inset(0 0 0 100%); opacity: .2; } to { clip-path: inset(0 0 0 0); opacity: 1; } }
@keyframes hs-shimmer { from { background-position: 220% 0; } to { background-position: -220% 0; } }
@keyframes hs-sweep { 0% { transform: translateX(-130%); } 22%, 100% { transform: translateX(130%); } }
@keyframes hs-draw { to { stroke-dashoffset: 0; } }
@keyframes hs-ring { from { stroke-dashoffset: 100; } }
@keyframes hs-grow { from { transform: scaleX(0); } }
@keyframes hs-tile { 0% { transform: translateX(-160%); } 30%, 100% { transform: translateX(260%); } }
@keyframes hs-ripple-gold { 0% { transform: scale(1); opacity: .9; } 100% { transform: scale(1.35); opacity: 0; } }
@keyframes hs-turn { to { transform: rotate(360deg); } }
@keyframes hs-drift { 0% { transform: translate3d(0,0,0) scale(1); } 100% { transform: translate3d(-4%,3%,0) scale(1.08); } }
@keyframes hs-spin { to { transform: rotate(360deg); } }
@keyframes hs-breathe { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
@keyframes hs-ripple { 0% { box-shadow: 0 0 0 0 rgba(138,21,56,.55); } 100% { box-shadow: 0 0 0 9px rgba(138,21,56,0); } }
@keyframes hs-live { 0% { box-shadow: 0 0 0 0 rgba(35,130,76,.55); } 100% { box-shadow: 0 0 0 8px rgba(35,130,76,0); } }
@keyframes hs-typing { 0%, 80%, 100% { opacity: .3; transform: none; } 40% { opacity: 1; transform: translateY(-3px); } }
@media (min-width: 901px) { body .gradio-container.gradio-container .tab-wrapper { margin-top: -62px !important; } }
@media (max-width: 900px) {
  body .gradio-container.gradio-container { padding: 0 16px 64px !important; }
  body .gradio-container.gradio-container .tab-wrapper { margin: 0 auto 28px !important; top: 10px; }
  body .gradio-container.gradio-container .tab-wrapper { width: 100% !important; }
  body .gradio-container.gradio-container .tab-container[role=tablist] { width: 100%; justify-content: space-between; }
  body .gradio-container.gradio-container .tab-container[role=tablist] { overflow-x: auto; scrollbar-width: none; }
  body .gradio-container.gradio-container .tab-container[role=tablist] button { padding: 7px 9px 6px !important; font-size: 12px !important; }
  body .gradio-container.gradio-container textarea, body .gradio-container.gradio-container input[type=text] { font-size: 16px !important; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
  body .gradio-container.gradio-container .serr path { stroke-dashoffset: 0; }
}
"""


def _scope(css: str, prefix: str) -> str:
    """Prefix every selector with `prefix`, descending into @media blocks."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        head = css[i:j].strip()
        depth, k = 1, j + 1
        while depth and k < n:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        body = css[j + 1:k - 1]
        if head.startswith("@media") or head.startswith("@supports"):
            # gradio emits media rules before base rules, so media rules need one more class to win
            out.append(f"{head}{{{_scope(body, prefix + '.gradio-container')}}}")
        elif head.startswith("@"):
            out.append(f"{head}{{{body}}}")
        elif head:
            sels = ", ".join(s.strip() if s.strip().startswith(":root") else f"{prefix} {s.strip()}"
                             for s in head.split(","))
            out.append(f"{sels}{{{body}}}")
        i = k
    return "\n".join(out)


def _fill(css: str) -> str:
    return (css.replace("UI_FONT", UI_FONT).replace("ACCENT_GRAD", ACCENT_GRAD).replace("GOLD_GRAD", GOLD_GRAD)
            .replace("KHATAM", _KHATAM_TILE).replace("GRAIN", _GRAIN))


def _split_media(css: str) -> tuple[str, str]:
    """Separate top-level @media blocks. Gradio rewrites media rules from launch(css=) with a prefix that never
    matches, so they are served through HEAD in a plain <style> tag instead."""
    rest, media, i, n = [], [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            rest.append(css[i:])
            break
        depth, k = 1, j + 1
        while depth and k < n:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        (media if css[i:j].strip().startswith("@media") else rest).append(css[i:k])
        i = k
    return "\n".join(rest), "\n".join(media)


CSS, MEDIA_CSS = _split_media(_fill(TOKENS + GRADIO_CSS + _scope(COMPONENT_CSS, "body .gradio-container") + KEYFRAMES))
HEAD += f"<style>{MEDIA_CSS}</style>"


# ---------------------------------------------------------------------------------------------
# Icons: 24px grid, 1.6 stroke, round caps. Outline only.
# ---------------------------------------------------------------------------------------------

_ICON_PATHS = {
    "arrow": "<path d='M5 12h14M13 6l6 6-6 6'/>",
    "check": "<path d='M5 12.5l4.5 4.5L19 7.5'/>",
    "lock": "<rect x='5' y='11' width='14' height='9.5' rx='2'/><path d='M8.5 11V8a3.5 3.5 0 0 1 7 0v3'/>",
    "shield": "<path d='M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3z'/><path d='M8.8 12.2l2.2 2.2 4.2-4.4'/>",
    "search": "<circle cx='11' cy='11' r='6.5'/><path d='M20 20l-4.2-4.2'/>",
    "chat": "<path d='M5 6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5v7a2.5 2.5 0 0 1-2.5 2.5H11l-4.5 4v-4A2.5 2.5 0 0 1 5 13.5z'/>",
    "link": "<path d='M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1'/><path d='M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1'/>",
    "x": "<path d='M6.5 6.5l11 11M17.5 6.5l-11 11'/>",
    "undo": "<path d='M9 14L4.5 9.5 9 5'/><path d='M4.5 9.5h10a5 5 0 0 1 0 10H12'/>",
    "clock": "<circle cx='12' cy='12' r='8.5'/><path d='M12 7.5V12l3 2'/>",
    "send": "<path d='M20 4L3.5 10.5l7 2.5 2.5 7z'/><path d='M20 4l-9.5 9'/>",
    "mail": "<rect x='3.5' y='5.5' width='17' height='13' rx='2'/><path d='M4 7l8 6 8-6'/>",
    "pen": "<path d='M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z'/><path d='M13.5 6.5l4 4'/>",
    "globe": "<circle cx='12' cy='12' r='8.5'/><path d='M3.5 12h17M12 3.5c2.4 2.4 3.5 5.3 3.5 8.5s-1.1 6.1-3.5 8.5c-2.4-2.4-3.5-5.3-3.5-8.5s1.1-6.1 3.5-8.5z'/>",
    "eye": "<path d='M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z'/><circle cx='12' cy='12' r='2.8'/>",
    "calendar": "<rect x='4' y='5' width='16' height='15' rx='2'/><path d='M4 10h16M9 3v4M15 3v4'/>",
    "help": "<circle cx='12' cy='12' r='8.5'/><path d='M9.6 9.5a2.5 2.5 0 0 1 4.8.9c0 1.7-2.4 2.2-2.4 3.8'/><path d='M12 17h.01'/>",
    "bulb": "<path d='M9.5 17.5h5M10.5 20.5h3'/><path d='M12 3.5a5.8 5.8 0 0 0-3.4 10.5c.6.5.9 1.1.9 1.8v.2h5v-.2c0-.7.3-1.3.9-1.8A5.8 5.8 0 0 0 12 3.5z'/>",
    "users": "<circle cx='9' cy='8.5' r='3.3'/><path d='M3 19.5a6 6 0 0 1 12 0'/><path d='M15.5 5.3a3.3 3.3 0 0 1 0 6.4M21 19.5a6 6 0 0 0-3.8-5.6'/>",
    "bolt": "<path d='M13 3L5.5 13.5h6L10.5 21 18.5 10h-6z'/>",
    "alert": "<circle cx='12' cy='12' r='8.5'/><path d='M12 8v4.5M12 16h.01'/>",
    "doc": "<path d='M7 3.5h7l4.5 4.5v12.5H7z'/><path d='M14 3.5V8h4.5M9.5 12.5h6M9.5 16h6'/>",
    "pin": "<path d='M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z'/><circle cx='12' cy='10' r='2.3'/>",
    "chevron": "<path d='M7 10l5 5 5-5'/>",
    "agree": "<circle cx='12' cy='12' r='8.5'/><path d='M8.5 12.3l2.4 2.4 4.6-4.9'/>",
    "star8": "<path d='M12 3l2.6 3.4 4.3-.5-.5 4.3L21 12l-2.6 1.8.5 4.3-4.3-.5L12 21l-2.6-3.4-4.3.5.5-4.3L3 12l2.6-1.8-.5-4.3 4.3.5z'/>",
}


def icon(name: str, cls: str = "") -> str:
    return f"<svg class='ic {cls}' viewBox='0 0 24 24' aria-hidden='true'>{_ICON_PATHS[name]}</svg>"


# The logo mark on the night ground: gold and maroon halves joined along the flag's serrated edge.
MARK = ("<svg viewBox='0 0 32 32' aria-hidden='true'><defs><clipPath id='hs-c'><circle cx='16' cy='16' r='15'/></clipPath>"
        "<linearGradient id='hs-mg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#E9C47C'/>"
        "<stop offset='1' stop-color='#B07A2A'/></linearGradient></defs><g clip-path='url(#hs-c)'>"
        "<path fill='url(#hs-mg)' d='M0 0H16L19.5 4 12.5 8 19.5 12 12.5 16 19.5 20 12.5 24 19.5 28 16 32H0Z'/>"
        "<path fill='#8A1538' d='M32 0H16L19.5 4 12.5 8 19.5 12 12.5 16 19.5 20 12.5 24 19.5 28 16 32H32Z'/>"
        "<path fill='none' stroke='#FFFFFF' stroke-width='1.6' stroke-linejoin='round' "
        "d='M16 0L19.5 4 12.5 8 19.5 12 12.5 16 19.5 20 12.5 24 19.5 28 16 32'/></g></svg>")

# Shared gradient for score rings (referenced by url(#hs-gold)); emitted once in the header.
SVG_DEFS = ("<svg width='0' height='0' style='position:absolute' aria-hidden='true'><defs>"
            "<linearGradient id='hs-gold' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#E9C47C'/>"
            "<stop offset='.55' stop-color='#C99A45'/><stop offset='1' stop-color='#8A1538'/></linearGradient></defs></svg>")

# The khatam: two squares turned against each other, the eight-point star of Gulf architecture.
KHATAM = ("<svg class='khatam' viewBox='0 0 100 100' aria-hidden='true'><g fill='none' stroke='currentColor' stroke-width='.35'>"
          "<rect x='18' y='18' width='64' height='64'/><rect x='18' y='18' width='64' height='64' transform='rotate(45 50 50)'/>"
          "<rect x='28' y='28' width='44' height='44'/><rect x='28' y='28' width='44' height='44' transform='rotate(45 50 50)'/>"
          "<circle cx='50' cy='50' r='15'/><circle cx='50' cy='50' r='45'/></g></svg>")

# Nine points, like the flag.
SERRATION = ("<svg class='serr {cls}' viewBox='0 0 56 8' aria-hidden='true'><path d='M1 7"
             + "".join(f"L{3 + 6 * i} 1L{6 + 6 * i} 7" for i in range(9)) + "'/></svg>")


def serration(cls: str = "") -> str:
    return SERRATION.replace("{cls}", cls)


def art(word: str) -> str:
    """A large outlined Ruqaa word behind a page title."""
    return f"<span class='art' lang='ar' dir='rtl' aria-hidden='true'>{word}</span>"


# ---------------------------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------------------------

def esc(text: str | None) -> str:
    return html.escape(text or "")


def initials(name: str) -> str:
    parts = [p for p in (name or "?").replace("-", " ").split() if p[:1].isalpha()]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def avatar(name: str, size: str = "", me: bool = False) -> str:
    return f"<div class='av {size}{' me' if me else ''}' aria-hidden='true'>{esc(initials(name))}</div>"


def score(n: int, label: str = "fit", size: str = "") -> str:
    n = max(0, min(100, int(n)))
    return (f"<div class='score {size}' aria-label='Fit score {n} of 100'><svg viewBox='0 0 36 36'>"
            f"<circle class='bg' cx='18' cy='18' r='16' pathLength='100'/>"
            f"<circle class='fg' cx='18' cy='18' r='16' pathLength='100' style='stroke-dashoffset:{100 - n}'/></svg>"
            f"<b data-count='{n}'>{n}</b><span>{label}</span></div>")


def tag(text: str, kind: str = "") -> str:
    return f"<span class='tag {kind}'>{text}</span>"


chip = tag


def dot(kind: str = "") -> str:
    return f"<span class='dot {kind}'></span>"


def empty(icon_name: str, title: str, body: str) -> str:
    return f"<div class='empty rise'><div class='ico'>{icon(icon_name)}</div><h3>{title}</h3><p>{body}</p></div>"


def status(text: str, kind: str = "") -> str:
    return f"<div class='status {kind}' role='status'>{dot()}<span>{text}</span></div>" if text else ""


def spinner_line(text: str) -> str:
    return f"<span class='loading'><span class='spin'></span>{text}</span>"


def typing() -> str:
    return "<span class='typing' aria-hidden='true'><i></i><i></i><i></i></span>"


def brand_bar(presenter: bool = False, account: str = "", place: str = "") -> str:
    pdot = "<span class='pdot' title='Presenter mode'></span>" if presenter else ""
    right = account or (f"<span class='place'>{icon('pin', 'sm')}{place}</span>" if place else "")
    return (f"{SVG_DEFS}<header class='top'><div class='logo'><span class='mark'>{MARK}{pdot}</span>"
            f"<span class='wm'>Handshake</span><span class='wm-ar' lang='ar'>مصافحة</span></div>"
            f"<div class='right'>{right}</div></header>")


# Rich HTML lists report clicks on [data-act] elements back to Python. Delegation on the container
# survives every re-render of the HTML inside it. Enter and Space work on focusable rows too.
DELEGATE_JS = """
const fire = (t) => trigger('click', {act: t.dataset.act, id: t.dataset.id || ''});
element.addEventListener('click', (e) => {
  const t = e.target.closest('[data-act]');
  if (!t || !element.contains(t) || t.tagName === 'SUMMARY') return;
  e.preventDefault();
  fire(t);
});
element.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter' && e.key !== ' ') return;
  const t = e.target.closest('[data-act]');
  if (!t || !element.contains(t) || t.tagName === 'BUTTON') return;
  e.preventDefault();
  fire(t);
});
"""

SHIELD = icon("shield", "sm")


def strip_emoji(text: str) -> str:
    """Drop emoji from model or legacy text that reaches the UI."""
    return re.sub("[\U0001F300-\U0001FAFF☀-➿️]", "", text or "").strip()
