"""Fahem & Wasel theme: the bright (light) version of the community Gradio theme "wood".

Source theme: amitguptaforwork/wood, theme_schema@0.0.2.json, Apache-2.0.
https://huggingface.co/spaces/amitguptaforwork/wood
Wood is gr.themes.Base with the stone palette, body_background_fill set to neutral_100, and
blocks filled with a wood photo hotlinked from Pinterest. This file rebuilds those values in code,
so the app makes no Hub request at boot, and replaces the photo with an original texture
(brand/assets/wood-bright.jpg, made by scripts/make_wood_texture.py).

Changes from wood, each with its reason:
- text_size: text_lg (16px body) instead of text_md (14px). iOS Safari zooms the page when a
  focused input is under 16px, and the demo may run on a phone.
- body_text_color_subdued: neutral_600 instead of neutral_400. neutral_400 on neutral_100 is
  2.31:1; neutral_600 is 6.99:1.
- block_label_text_color: neutral_600 instead of neutral_500 (4.59:1 on neutral_50, now 7.3:1).
- input_border_width 1px, input_border_color neutral_500: wood draws inputs with no border, so a
  text box on a white surface has no visible edge.
- Primary buttons neutral_800 (hover neutral_700) instead of primary_500: team decision,
  2026-11-06. White on neutral_800 is 15.17:1.
- The chatbot is a white card, not a wood block: team decision, 2026-11-06. See .fw-chat below.
- Light mode only. Wood's dark values put the dark agent color on a dark ground (1.26:1).

Replaces gr.themes.Soft in ui.py. Tested on gradio 6.31.0. In gradio 6, theme, css, head and js
go to launch(); in gradio 5 and earlier they go to gr.Blocks().
"""

from pathlib import Path

import gradio as gr
from gradio.themes.utils import colors, sizes

ASSETS = Path(__file__).parent / "assets"
gr.set_static_paths(paths=[ASSETS])

# Served by gradio once the folder is a static path. Absolute from the site root.
WOOD_URL = f"/gradio_api/file={(ASSETS / 'wood-bright.jpg').as_posix()}"
# To use wood's original photo instead (license unknown, loads from Pinterest), set:
# WOOD_URL = "https://i.pinimg.com/736x/9c/34/c9/9c34c9e5029b562c55b253740fac55c1.jpg"

# Tokens. Names match the "Fahem & Wasel Brand Kit" design system. Values are stone, from wood.
FW = {
    "fw-ink": "#292524",          # stone-800. Body text. 15.17:1 on white, 11.12:1 on darkest wood pixel
    "fw-ink-2": "#57534e",        # stone-600. Secondary text. 7.63:1 white, 5.59:1 wood
    "fw-control-edge": "#78716c", # stone-500. Input and outline-button edges. 4.80:1 on white
    "fw-line": "#d6d3d1",         # stone-300. Decorative hairlines only, never a control edge
    "fw-paper": "#ffffff",        # card surface
    "fw-paper-2": "#f5f5f4",      # stone-100. Page ground, quote ground, founder chat bubble
    "fw-paper-3": "#e7e5e4",      # stone-200. Tag, badge and secondary button ground
    "fw-primary": "#292524",      # stone-800. Primary button. White text 15.17:1
    "fw-primary-hover": "#44403c",# stone-700. White text 10.27:1
    "fw-fahem": "#292524",        # Fahem: dark. L* 16
    "fw-on-fahem": "#ffffff",     # 15.17:1 on fw-fahem
    "fw-wasel": "#fafaf9",        # Wasel: light, always with fw-wasel-edge. L* 98
    "fw-wasel-edge": "#292524",   # 2px edge that gives the light panel its shape
    "fw-on-wasel": "#292524",     # 14.52:1 on fw-wasel
    "fw-danger": "#b91c1c",       # wood's error color. 6.47:1 on white
    "fw-focus": "#292524",        # 2px focus ring, 2px offset
}

THEME = gr.themes.Base(
    primary_hue=colors.stone,
    secondary_hue=colors.stone,
    neutral_hue=colors.stone,
    text_size=sizes.text_lg,
    spacing_size=sizes.spacing_md,
    radius_size=sizes.radius_md,
    font=[
        gr.themes.GoogleFont("IBM Plex Sans", weights=(400, 600)),
        gr.themes.GoogleFont("IBM Plex Sans Arabic", weights=(400, 600)),
        "ui-sans-serif", "system-ui", "sans-serif",
    ],
    font_mono=[
        gr.themes.GoogleFont("IBM Plex Mono", weights=(400, 600)),
        "ui-monospace", "Consolas", "monospace",
    ],
).set(
    # wood values
    body_background_fill="*neutral_100",
    background_fill_secondary="*primary_50",
    block_background_fill=f"url('{WOOD_URL}') repeat, #f3ebde",
    block_border_color="*neutral_200",
    block_border_width="1px",
    block_radius="*radius_sm",
    block_shadow="none",
    block_label_background_fill="*neutral_50",
    button_secondary_background_fill="*neutral_200",
    button_secondary_background_fill_hover="*neutral_300",
    button_secondary_text_color="*neutral_900",
    button_large_radius="*radius_md",
    button_medium_radius="*radius_md",
    button_large_text_weight="600",
    input_background_fill="*neutral_100",
    input_radius="*radius_sm",
    color_accent="*primary_500",
    color_accent_soft="*primary_50",
    link_text_color="*secondary_600",
    # changes, see module docstring
    button_primary_background_fill="*neutral_800",
    button_primary_background_fill_hover="*neutral_700",
    button_primary_text_color="white",
    body_text_color="*neutral_800",
    body_text_color_subdued="*neutral_600",
    block_title_text_color="*neutral_600",
    block_info_text_color="*neutral_600",
    input_border_width="1px",
    input_border_color="*neutral_500",
    input_border_color_focus="*neutral_800",
    input_placeholder_color="*neutral_500",
    block_label_text_color="*neutral_600",
)

# Loads IBM Plex Sans italic for quotes. The theme's GoogleFont loads upright weights only.
HEAD = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=IBM+Plex+Sans:ital,wght@1,400&display=swap">'
)

# Light mode only: reload once with ?__theme=light when the browser prefers dark.
FORCE_LIGHT_JS = """
() => {
  const url = new URL(window.location);
  if (url.searchParams.get('__theme') !== 'light') {
    url.searchParams.set('__theme', 'light');
    window.location.replace(url.href);
  }
}
"""

_VARS = ";".join(f"--{k}:{v}" for k, v in FW.items())

# Every selector starts with "body .fw": put elem_classes=["fw"] on each screen's outer gr.Column.
COMPONENT_CSS = r"""
body .fw *,body .fw *::before,body .fw *::after{box-sizing:border-box}
body .fw{font-family:'IBM Plex Sans','IBM Plex Sans Arabic',ui-sans-serif,system-ui,sans-serif;color:var(--fw-ink);font-size:16px;line-height:24px}
body .fw :focus-visible{outline:2px solid var(--fw-focus);outline-offset:2px}
/* gradio 6.31 sets color on every element in gr.HTML via ".gradio-container-6-31-0 .prose *" (0,2,0).
   This rule (0,2,1) makes text inside brand components inherit instead; brand rules below are (0,3,1). */
body .fw :is(.fw-wordmark,.fw-agent,.fw-state,.fw-progress,.fw-field,.fw-flag,.fw-quote,.fw-tag,.fw-score,.fw-demo,.fw-match,.fw-intro,.fw-contact) *{color:inherit}

/* wordmark */
body .fw .fw-wordmark{font-size:20px;line-height:26px;font-weight:600}

/* agent header: names only, no marks. Fahem dark, Wasel light with a 2px edge */
body .fw .fw-agent{display:flex;align-items:center;gap:var(--fw-space-3);padding:var(--fw-space-3) var(--fw-space-4);border-radius:var(--fw-radius-lg);border:2px solid var(--fw-wasel-edge)}
body .fw .fw-agent--fahem{background:var(--fw-fahem);color:var(--fw-on-fahem);border-color:var(--fw-fahem)}
body .fw .fw-agent--wasel{background:var(--fw-wasel);color:var(--fw-on-wasel)}
body .fw .fw-agent__text{display:flex;flex-direction:column;min-width:0;flex:1}
body .fw .fw-agent__name{font-size:20px;line-height:26px;font-weight:600}
body .fw .fw-agent__sub{font-size:14px;line-height:20px}
body .fw .fw-agent--fahem .fw-agent__sub{color:#e7e5e4}
body .fw .fw-agent--wasel .fw-agent__sub{color:var(--fw-ink-2)}

/* state chip, inside the agent header */
body .fw .fw-state{display:inline-flex;align-items:center;gap:6px;font-size:13px;line-height:16px;font-weight:600;padding:4px 10px;border-radius:var(--fw-radius-full);white-space:nowrap}
body .fw .fw-agent--fahem .fw-state{background:#44403c;color:#ffffff}
body .fw .fw-agent--wasel .fw-state{background:var(--fw-paper-3);color:var(--fw-ink)}
body .fw .fw-state__dot{width:8px;height:8px;border-radius:50%;background:currentColor}
body .fw .fw-state--listening .fw-state__dot{animation:fw-pulse 1.2s ease-in-out infinite}
body .fw .fw-state--thinking .fw-state__dot{animation:fw-blink 1s steps(2,start) infinite}
@keyframes fw-pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.6)}}
@keyframes fw-blink{to{visibility:hidden}}

/* chat: gr.Chatbot(elem_classes=["fw-chat"]) and its input row gr.Row(elem_classes=["fw-chat-input"]).
   A white card, not a wood block. Fahem turns are plain text; founder turns are a light bubble.
   .bot, .user and .message are gradio 6.31 class names. */
body .fw .fw-chat,body .fw .fw-chat-input{background:var(--fw-paper) !important;border:1px solid var(--fw-line) !important;box-shadow:none !important}
body .fw .fw-chat{border-radius:var(--fw-radius-lg) var(--fw-radius-lg) 0 0 !important;border-bottom:0 !important}
body .fw .fw-chat-input{border-radius:0 0 var(--fw-radius-lg) var(--fw-radius-lg) !important;padding:8px !important;gap:8px !important;align-items:center;margin-top:calc(-1 * var(--layout-gap)) !important}
body .fw .fw-chat .message-wrap{gap:10px !important;padding:16px !important}
body .fw .fw-chat .bot-row{max-width:80% !important}
body .fw .fw-chat .user-row{max-width:70% !important}
body .fw .fw-chat .message{max-width:100% !important;box-shadow:none !important}
body .fw .fw-chat .bot{background:transparent !important;border:0 !important;color:var(--fw-ink) !important;padding:0 !important}
body .fw .fw-chat .user{background:var(--fw-paper-2) !important;border:0 !important;color:var(--fw-ink) !important;padding:8px 12px !important;border-radius:var(--fw-radius-lg) !important}
body .fw .fw-chat-input .block{background:transparent !important;border:0 !important;box-shadow:none !important;padding:0 !important}
body .fw .fw-chat-input textarea,body .fw .fw-chat-input input{border:0 !important;background:transparent !important;box-shadow:none !important}
/* gr.Audio(elem_classes=["fw-mic"]): gradio draws its record dot with --primary-600 */
body .fw .fw-mic{--primary-600:var(--fw-fahem);background:transparent !important;border:0 !important}
body .fw .fw-mic .record-button{border:1px solid var(--fw-fahem) !important;font-weight:600}

/* topic progress */
body .fw .fw-progress{display:flex;flex-direction:column;gap:6px}
body .fw .fw-progress__label{font-size:14px;line-height:20px;color:var(--fw-ink-2)}
body .fw .fw-progress__label b{color:var(--fw-ink);font-weight:600}
body .fw .fw-progress__track{display:flex;gap:3px}
body .fw .fw-progress__seg{flex:1;height:6px;border-radius:var(--fw-radius-full);background:var(--fw-paper-3);border:1px solid var(--fw-line)}
body .fw .fw-progress__seg--done{background:var(--fw-fahem);border-color:var(--fw-fahem)}
body .fw .fw-progress__seg--now{background:var(--fw-control-edge);border-color:var(--fw-control-edge)}

/* profile field row */
body .fw .fw-field{display:flex;flex-direction:column;gap:6px;padding:var(--fw-space-3) var(--fw-space-4);background:var(--fw-paper);border:1px solid var(--fw-line);border-radius:var(--fw-radius-lg)}
body .fw .fw-field__head{display:flex;justify-content:space-between;align-items:center;gap:var(--fw-space-2)}
body .fw .fw-field__label{font-size:14px;line-height:20px;font-weight:600;color:var(--fw-ink-2)}
body .fw .fw-field__value{font-size:16px;line-height:24px;font-weight:600}
body .fw .fw-field__empty{font-size:16px;line-height:24px;color:var(--fw-ink-2)}
body .fw .fw-field--check{border:2px dashed var(--fw-control-edge)}
body .fw .fw-flag{font-size:13px;line-height:16px;font-weight:600;padding:2px 8px;border-radius:var(--fw-radius-full);border:1px dashed var(--fw-control-edge);color:var(--fw-ink);background:var(--fw-paper-2);white-space:nowrap}

/* quote citation: the founder's own words, shown by Fahem and Wasel */
body .fw .fw-quote{display:flex;gap:6px;font-size:14px;line-height:20px;background:var(--fw-paper-2);border-radius:var(--fw-radius-md);padding:6px 10px;color:var(--fw-ink-2)}
body .fw .fw-quote__mark{font-size:20px;line-height:20px;font-weight:600;color:var(--fw-ink);flex:none}
body .fw .fw-quote__who{font-weight:600;color:var(--fw-ink);font-style:normal}
body .fw .fw-quote__text{font-style:italic}
body .fw .fw-quote--edited{font-style:normal}

/* category tag, fit score, demo badge */
body .fw .fw-tags{display:flex;flex-wrap:wrap;gap:6px}
body .fw .fw-tag{display:inline-flex;align-items:center;font-size:13px;line-height:16px;font-weight:600;padding:4px 10px;border-radius:var(--fw-radius-full);background:var(--fw-paper-3);color:var(--fw-ink)}
body .fw .fw-score{display:inline-flex;align-items:baseline;gap:4px;background:var(--fw-fahem);color:var(--fw-on-fahem);border-radius:var(--fw-radius-full);padding:4px 12px;white-space:nowrap}
body .fw .fw-score__label{font-size:13px;line-height:16px}
body .fw .fw-score__value{font-size:18px;line-height:20px;font-weight:600}
body .fw .fw-demo{display:inline-flex;align-items:center;font-size:13px;line-height:16px;font-weight:600;padding:3px 9px;border-radius:var(--fw-radius-sm);border:1px dashed var(--fw-control-edge);color:var(--fw-ink-2);background:var(--fw-paper)}

/* match card */
body .fw .fw-match{display:flex;flex-direction:column;gap:var(--fw-space-3);background:var(--fw-paper);border:1px solid var(--fw-line);border-radius:var(--fw-radius-lg);padding:var(--fw-space-4)}
body .fw .fw-match__head{display:flex;align-items:flex-start;gap:var(--fw-space-3)}
body .fw .fw-initials{flex:none;width:48px;height:48px;border-radius:var(--fw-radius-full);background:var(--fw-paper-3);display:inline-flex;align-items:center;justify-content:center;font-weight:600}
body .fw .fw-match__who{display:flex;flex-direction:column;gap:4px;min-width:0;flex:1}
body .fw .fw-match__name{font-size:20px;line-height:26px;font-weight:600}
body .fw .fw-match__summary{font-size:14px;line-height:20px;color:var(--fw-ink-2)}
body .fw .fw-reasons{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:var(--fw-space-3)}
body .fw .fw-reason{display:flex;flex-direction:column;gap:6px}
body .fw .fw-reason__text{font-size:16px;line-height:24px}
body .fw .fw-concern{font-size:14px;line-height:20px;color:var(--fw-ink-2);border-top:1px solid var(--fw-line);padding-top:var(--fw-space-2);margin:0}
body .fw .fw-match__note{font-size:14px;line-height:20px;color:var(--fw-ink-2);margin:0}

/* intro request card and contact card */
body .fw .fw-intro,body .fw .fw-contact{display:flex;flex-direction:column;gap:var(--fw-space-3);background:var(--fw-paper);border:1px solid var(--fw-line);border-radius:var(--fw-radius-lg);padding:var(--fw-space-4)}
body .fw .fw-intro__title,body .fw .fw-contact__title{font-size:18px;line-height:24px;font-weight:600}
body .fw .fw-intro__by{font-size:14px;line-height:20px;color:var(--fw-ink-2)}
body .fw .fw-contact__status{display:flex;align-items:center;gap:6px;font-size:14px;line-height:20px;font-weight:600}
body .fw .fw-contact__rows{display:grid;grid-template-columns:auto 1fr;gap:4px var(--fw-space-3);font-size:16px;line-height:24px;margin:0}
body .fw .fw-contact__rows dt{color:var(--fw-ink-2)}
body .fw .fw-contact__rows dd{margin:0;font-weight:600;overflow-wrap:anywhere}

/* landing and sign-up only: two headings above the kit scale */
body .fw .fw-hero{font-size:56px;line-height:64px;font-weight:600;letter-spacing:-0.01em;margin:0}
body .fw .fw-section-title{font-size:40px;line-height:48px;font-weight:600;margin:0}

@media (prefers-reduced-motion:reduce){body .fw .fw-state__dot{animation:none}}
"""

CSS = (
    ":root{" + _VARS + ";--fw-radius-sm:4px;--fw-radius-md:6px;--fw-radius-lg:8px;--fw-radius-full:999px;"
    "--fw-space-1:4px;--fw-space-2:8px;--fw-space-3:12px;--fw-space-4:16px;--fw-space-6:24px;--fw-space-8:32px}"
    + COMPONENT_CSS
)


def launch_kwargs() -> dict:
    """Gradio 6: demo.launch(**launch_kwargs()). Gradio 5 and earlier: pass these to gr.Blocks()."""
    return {"theme": THEME, "css": CSS, "head": HEAD, "js": FORCE_LIGHT_JS}
