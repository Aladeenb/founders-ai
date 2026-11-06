"""Generate the Fahem & Wasel character art (Notion-style line portraits) and the animated duo scene.
Usage: python3 design/fahem-wasel/generate.py design/fahem-wasel
"""
import sys
from pathlib import Path

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
INK, PAPER, WHITE = '#1B1B1F', '#FBF8F3', '#FFFFFF'
BLUE, BLUE_TINT = '#2E4FC8', '#E4EAFB'
ORANGE, ORANGE_TINT = '#D2591C', '#FCE6D6'
SW = 3.2  # the one stroke weight for every line
THICK = 'stroke-width="3.6"'

def stroke(extra=''):
    width = '' if 'stroke-width' in extra else f'stroke-width="{SW}" '
    return f'stroke="{INK}" {width}stroke-linecap="round" stroke-linejoin="round" {extra}'

# ---------- Fahem: the one who understands (ghutra and agal, glasses, full beard, blue pen) ----------
def fahem_parts(prefix=''):
    shoulders = f'''<path d="M34 244 C 40 200 78 182 120 182 C 162 182 200 200 206 244 Z" fill="{WHITE}" {stroke()}/>
<path d="M120 192 V 240" fill="none" {stroke()}/>
<path d="M131 224 L 135 204" fill="none" stroke="{BLUE}" stroke-width="6" stroke-linecap="round"/>
<path d="M128 210 H 140" fill="none" {stroke('stroke-width="2.6"')}/>'''
    neck = f'<path d="M106 156 V 184 C 112 191 128 191 134 184 V 156" fill="{WHITE}" {stroke()}/>'
    drape = f'''<path fill-rule="evenodd" d="M120 50 C 96 50 78 66 72 92 C 66 120 66 160 58 196 C 54 214 44 230 30 248 L 210 248 C 196 230 186 214 182 196 C 174 160 174 120 168 92 C 162 66 144 50 120 50 Z M92 126 C 96 148 104 166 102 186 C 100 206 96 226 92 248 L 148 248 C 144 226 140 206 138 186 C 136 166 144 148 148 126 Z" fill="{WHITE}" {stroke()}/>
<path d="M76 128 C 72 158 68 188 58 214 M164 128 C 168 158 172 188 182 214" fill="none" {stroke('opacity="0.5"')}/>'''
    face = f'<path d="M88 114 C 88 88 102 74 120 74 C 138 74 152 88 152 114 C 152 142 138 160 120 160 C 102 160 88 142 88 114 Z" fill="{WHITE}" {stroke()}/>'
    beard = f'''<path d="M90 124 C 92 150 105 166 120 166 C 135 166 148 150 150 124 C 146 132 140 136 134 137 C 128 133 112 133 106 137 C 100 136 94 132 90 124 Z" fill="{INK}"/>
<path class="{prefix}mouth" d="M111 149 C 115 153 125 153 129 149" fill="none" stroke="{WHITE}" stroke-width="3" stroke-linecap="round"/>'''
    front = f'<path d="M84 106 C 84 76 100 60 120 60 C 140 60 156 76 156 106 C 146 94 134 89 120 89 C 106 89 94 94 84 106 Z" fill="{WHITE}" {stroke()}/>'
    agal = f'''<path d="M83 80 C 97 64 143 64 157 80" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>
<path d="M86 70 C 100 55 140 55 154 70" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'''
    brows = f'<path d="M98 101 Q 106 96 114 99 M126 99 Q 134 96 142 101" fill="none" {stroke()}/>'
    eyes = f'''<g class="{prefix}eyes"><circle cx="106" cy="116" r="2.8" fill="{INK}"/><circle cx="134" cy="116" r="2.8" fill="{INK}"/></g>'''
    glasses = f'''<circle cx="106" cy="114" r="11" fill="none" {stroke('stroke-width="2.8"')}/><circle cx="134" cy="114" r="11" fill="none" {stroke('stroke-width="2.8"')}/>
<path d="M117 112 Q 120 109 123 112 M95 112 L 89 109 M145 112 L 151 109" fill="none" {stroke('stroke-width="2.6"')}/>'''
    nose = f'<path d="M120 117 C 118 124 116 129 121 130" fill="none" {stroke()}/>'
    head = f'<g class="{prefix}head">{drape}{face}{beard}{front}{agal}{brows}{eyes}{glasses}{nose}</g>'
    return shoulders, neck, head

# ---------- Wasel: the one who connects (quiff, boxed beard, grin, orange earbud and link pin) ----------
def wasel_parts(prefix=''):
    shoulders = f'''<path d="M34 244 C 40 200 78 182 120 182 C 162 182 200 200 206 244 Z" fill="{WHITE}" {stroke()}/>
<path d="M120 196 V 240" fill="none" {stroke()}/>
<path d="M104 181 L 110 202 L 120 194 L 130 202 L 136 181" fill="{WHITE}" {stroke()}/>
<circle cx="120" cy="210" r="2.4" fill="{INK}"/><circle cx="120" cy="226" r="2.4" fill="{INK}"/>
<circle cx="154" cy="210" r="11" fill="{ORANGE}" {stroke('stroke-width="2.6"')}/>
<path d="M149 212 a3.5 3.5 0 0 1 0 -5 l2 -2 a3.5 3.5 0 0 1 5 5 M159 208 a3.5 3.5 0 0 1 0 5 l-2 2 a3.5 3.5 0 0 1 -5 -5" fill="none" stroke="{WHITE}" stroke-width="2" stroke-linecap="round"/>'''
    neck = f'<path d="M106 154 V 184 C 112 191 128 191 134 184 V 154" fill="{WHITE}" {stroke()}/>'
    ears = f'''<path d="M88 110 C 78 108 78 128 89 128" fill="{WHITE}" {stroke()}/>
<path d="M152 110 C 162 108 162 128 151 128" fill="{WHITE}" {stroke()}/>
<g class="{prefix}bud"><circle cx="158" cy="121" r="5.5" fill="{ORANGE}" {stroke('stroke-width="2.4"')}/><path d="M158 127 V 138" stroke="{ORANGE}" stroke-width="5" stroke-linecap="round"/></g>'''
    face = f'<path d="M88 112 C 88 86 102 70 120 70 C 138 70 152 86 152 112 C 152 142 138 160 120 160 C 102 160 88 142 88 112 Z" fill="{WHITE}" {stroke()}/>'
    hair = f'''<path d="M84 108 C 78 78 94 50 124 48 C 152 47 166 70 156 104 C 152 92 146 85 138 82 C 128 92 108 92 98 84 C 92 90 88 98 84 108 Z" fill="{INK}"/>
<path d="M110 60 C 120 55 132 56 140 62" fill="none" stroke="{WHITE}" stroke-width="2.4" stroke-linecap="round" opacity="0.9"/>'''
    beard = f'''<path d="M89 116 C 90 146 104 163 120 163 C 136 163 150 146 151 116 C 148 126 146 134 139 139 C 131 143 109 143 101 139 C 94 134 92 126 89 116 Z" fill="{INK}"/>
<path d="M104 134 C 112 129 128 129 136 134 C 128 136 112 136 104 134 Z" fill="{INK}"/>
<path class="{prefix}mouth" d="M106 141 C 109 158 131 158 134 141 Z" fill="{WHITE}" {stroke('stroke-width="2.6"')}/>'''
    brows = f'<path d="M98 97 Q 107 90 116 95 M124 95 Q 133 90 142 97" fill="none" {stroke(THICK)}/>'
    eyes = f'<g class="{prefix}eyes"><path d="M101 110 Q 106 104 111 110 M129 110 Q 134 104 139 110" fill="none" {stroke()}/></g>'
    nose = f'<path d="M120 112 C 123 119 122 124 117 125" fill="none" {stroke()}/>'
    head = f'<g class="{prefix}head">{ears}{face}{hair}{beard}{brows}{eyes}{nose}</g>'
    return shoulders, neck, head

def portrait(parts, tint, title, desc, clip_id):
    shoulders, neck, head = parts
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" role="img" aria-labelledby="{clip_id}-t {clip_id}-d">
<title id="{clip_id}-t">{title}</title><desc id="{clip_id}-d">{desc}</desc>
<defs><clipPath id="{clip_id}"><circle cx="120" cy="120" r="120"/></clipPath></defs>
<g clip-path="url(#{clip_id})"><rect width="240" height="240" fill="{tint}"/>{shoulders}{neck}{head}</g>
</svg>
'''

(OUT / 'fahem-portrait.svg').write_text(portrait(fahem_parts(), BLUE_TINT, 'Fahem · فاهم', 'Line portrait of Fahem: an older Qatari man in ghutra and agal with round glasses and a full beard, a blue pen in his thobe pocket.', 'fahem'))
(OUT / 'wasel-portrait.svg').write_text(portrait(wasel_parts(), ORANGE_TINT, 'Wasel · واصل', 'Line portrait of Wasel: a younger Qatari man with a black quiff, short boxed beard and a wide grin, an orange earbud and an orange link pin.', 'wasel'))

# ---------- The icons: a few hand-drawn strokes on a soft tile, one colour each (Jack & Jill simplicity, Qatari cue) ----------
TILE = '#F1EEE8'
LW = 1.8   # icon line weight at 64px: light, hand-drawn

# The final drawings live in characters.py (chosen in iterations.html: Fahem G + Wasel E).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from characters import fahem_icon, wasel_icon

def tile(icon, title, desc, idn, bg=TILE):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="{idn}-t {idn}-d">
<title id="{idn}-t">{title}</title><desc id="{idn}-d">{desc}</desc>
<defs><clipPath id="{idn}-clip"><rect width="64" height="64" rx="14"/></clipPath></defs>
<rect width="64" height="64" rx="14" fill="{bg}"/><g clip-path="url(#{idn}-clip)">{icon}</g>
</svg>
'''

(OUT / 'fahem.svg').write_text(tile(fahem_icon(), 'Fahem · فاهم', 'Fahem, from Qatar, in a few blue strokes: white cobra ghutra and agal, happy eyes, a warm smile.', 'fahem'))
(OUT / 'wasel.svg').write_text(tile(wasel_icon(), 'Wasel · واصل', 'Wasel, from Oman, in a few orange strokes: the embroidered kumma cap, a wink and an open smile.', 'wasel'))

# ---------- Logo mark: two speech bubbles that overlap into one conversation ----------
logo = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 72" role="img" aria-label="Fahem and Wasel mark">
<path d="M10 12 h36 a10 10 0 0 1 10 10 v14 a10 10 0 0 1 -10 10 h-18 l-10 9 v-9 h-8 a10 10 0 0 1 -10 -10 v-14 a10 10 0 0 1 10 -10 z" fill="{BLUE}"/>
<path d="M50 26 h36 a10 10 0 0 1 10 10 v14 a10 10 0 0 1 -10 10 h-8 v9 l-10 -9 h-18 a10 10 0 0 1 -10 -10 v-14 a10 10 0 0 1 10 -10 z" fill="{ORANGE}" style="mix-blend-mode:multiply"/>
<circle cx="22" cy="29" r="3" fill="{WHITE}"/><circle cx="32" cy="29" r="3" fill="{WHITE}"/>
<path d="M64 43 h18" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>
</svg>
'''
(OUT / 'mark.svg').write_text(logo)

# ---------- The animated duo: Fahem reads once and writes the card; Wasel searches the cards and connects ----------
duo = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 380" role="img" aria-labelledby="duo-t duo-d">
<title id="duo-t">Fahem and Wasel at work</title>
<desc id="duo-d">Fahem listens and writes a profile card. The card slides to Wasel, who connects it to two matching founders.</desc>
<style>
  * {{ transform-box: fill-box; }}
  .f-face {{ transform-origin: 50% 90%; animation: nod 8s ease-in-out infinite; }}
  .w-face {{ transform-origin: 50% 90%; animation: lean 8s ease-in-out infinite; }}
  .f-eyes, .w-eyes {{ transform-origin: 50% 50%; }}
  .f-eyes {{ animation: blinkA 8s infinite; }}
  .w-eyes {{ animation: blinkB 8s infinite; }}
  .bubble {{ transform-origin: 0% 100%; animation: bubble 8s ease-out infinite; }}
  .dot {{ animation: dots 0.9s ease-in-out infinite; }}
  .dot:nth-child(2) {{ animation-delay: .15s; }} .dot:nth-child(3) {{ animation-delay: .3s; }}
  .card {{ animation: card 8s cubic-bezier(.2,.8,.2,1) infinite; }}
  .write {{ stroke-dasharray: 120; animation: write 8s ease-out infinite; }}
  .write.l2 {{ animation-name: write2; }} .write.l3 {{ animation-name: write3; }}
  .thread {{ stroke-dasharray: 4 7; stroke-dashoffset: 260; animation: thread 8s ease-out infinite; }}
  .thread.t2 {{ animation-name: thread2; }}
  .match {{ transform-origin: 50% 50%; animation: match 8s cubic-bezier(.2,.8,.2,1) infinite; }}
  .match.m2 {{ animation-name: match2; }}
  .bud {{ }}
  @keyframes nod {{ 0%,4%,22%,100% {{ transform: rotate(0); }} 8% {{ transform: rotate(-3deg); }} 13% {{ transform: rotate(2deg); }} 18% {{ transform: rotate(-2deg); }} }}
  @keyframes lean {{ 0%,50%,80%,100% {{ transform: rotate(0); }} 56% {{ transform: rotate(-4deg); }} 66% {{ transform: rotate(3deg); }} }}
  @keyframes blinkA {{ 0%,33%,35%,82%,84%,100% {{ transform: scaleY(1); }} 34%,83% {{ transform: scaleY(.1); }} }}
  @keyframes blinkB {{ 0%,23%,25%,70%,72%,100% {{ transform: scaleY(1); }} 24%,71% {{ transform: scaleY(.1); }} }}
  @keyframes bubble {{ 0% {{ opacity: 0; transform: scale(.6); }} 4%,20% {{ opacity: 1; transform: scale(1); }} 25%,100% {{ opacity: 0; transform: scale(.9); }} }}
  @keyframes dots {{ 0%,100% {{ transform: translateY(0); opacity: .5; }} 50% {{ transform: translateY(-3px); opacity: 1; }} }}
  @keyframes card {{ 0%,18% {{ opacity: 0; transform: translate(0,10px); }} 23% {{ opacity: 1; transform: translate(0,0); }} 40% {{ transform: translate(0,0); }} 52%,90% {{ opacity: 1; transform: translate(78px,0); }} 97%,100% {{ opacity: 0; transform: translate(78px,0); }} }}
  @keyframes write {{ 0%,24% {{ stroke-dashoffset: 120; }} 30%,100% {{ stroke-dashoffset: 0; }} }}
  @keyframes write2 {{ 0%,28% {{ stroke-dashoffset: 120; }} 34%,100% {{ stroke-dashoffset: 0; }} }}
  @keyframes write3 {{ 0%,32% {{ stroke-dashoffset: 120; }} 38%,100% {{ stroke-dashoffset: 0; }} }}
  @keyframes thread {{ 0%,54% {{ stroke-dashoffset: 260; opacity: 1; }} 66%,90% {{ stroke-dashoffset: 0; opacity: 1; }} 97%,100% {{ opacity: 0; }} }}
  @keyframes thread2 {{ 0%,58% {{ stroke-dashoffset: 260; opacity: 1; }} 70%,90% {{ stroke-dashoffset: 0; opacity: 1; }} 97%,100% {{ opacity: 0; }} }}
  @keyframes match {{ 0%,64% {{ opacity: 0; transform: scale(.4); }} 69% {{ opacity: 1; transform: scale(1.12); }} 72%,90% {{ opacity: 1; transform: scale(1); }} 97%,100% {{ opacity: 0; }} }}
  @keyframes match2 {{ 0%,68% {{ opacity: 0; transform: scale(.4); }} 73% {{ opacity: 1; transform: scale(1.12); }} 76%,90% {{ opacity: 1; transform: scale(1); }} 97%,100% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{
    *, *::before {{ animation: none !important; }}
    .card {{ opacity: 1; transform: translate(78px,0); }} .write, .thread {{ stroke-dashoffset: 0; }} .match {{ opacity: 1; }} .bubble {{ opacity: 0; }}
  }}
</style>
<rect width="720" height="380" rx="28" fill="{PAPER}"/>
<g transform="translate(56 100) scale(2.4)"><defs><clipPath id="duoTileF"><rect width="64" height="64" rx="14"/></clipPath></defs><rect width="64" height="64" rx="14" fill="{BLUE_TINT}"/><g clip-path="url(#duoTileF)">{fahem_icon(BLUE,'f-',BLUE_TINT)}</g></g>
<g transform="translate(510 100) scale(2.4)"><defs><clipPath id="duoTileW"><rect width="64" height="64" rx="14"/></clipPath></defs><rect width="64" height="64" rx="14" fill="{ORANGE_TINT}"/><g clip-path="url(#duoTileW)">{wasel_icon(ORANGE,'w-',ORANGE_TINT)}</g></g>

<text x="133" y="300" text-anchor="middle" font-family="Instrument Serif, Georgia, serif" font-size="22" fill="{INK}">Fahem <tspan fill="{BLUE}" font-family="Reem Kufi, sans-serif" font-size="18">فاهم</tspan></text>
<text x="587" y="300" text-anchor="middle" font-family="Instrument Serif, Georgia, serif" font-size="22" fill="{INK}">Wasel <tspan fill="{ORANGE}" font-family="Reem Kufi, sans-serif" font-size="18">واصل</tspan></text>
<g class="bubble">
  <path d="M46 34 h86 a16 16 0 0 1 16 16 v14 a16 16 0 0 1 -16 16 h-58 l-14 14 v-14 h-14 a16 16 0 0 1 -16 -16 v-14 a16 16 0 0 1 16 -16 z" fill="{WHITE}" stroke="{BLUE}" stroke-width="{SW}" stroke-linejoin="round"/>
  <g fill="{BLUE}"><circle class="dot" cx="70" cy="57" r="5"/><circle class="dot" cx="89" cy="57" r="5"/><circle class="dot" cx="108" cy="57" r="5"/></g>
</g>

<g class="card">
  <g transform="translate(236 142) scale(0.9)">
    <rect width="112" height="140" rx="12" fill="{WHITE}" stroke="{INK}" stroke-width="{SW}"/>
    <path d="M0 12 a12 12 0 0 1 12 -12 h88 a12 12 0 0 1 12 12 v14 h-112 z" fill="{BLUE}"/>
    <circle cx="22" cy="52" r="10" fill="{BLUE_TINT}" stroke="{INK}" stroke-width="2.4"/>
    <path class="write" d="M40 48 h50" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>
    <path class="write l2" d="M40 58 h34" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" opacity=".5"/>
    <path class="write l3" d="M14 82 h84 M14 96 h70 M14 110 h78" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" opacity=".45"/>
    <path d="M14 124 h30" stroke="{BLUE}" stroke-width="3.2" stroke-linecap="round"/>
  </g>
</g>

<path class="thread" d="M416 176 C 444 150 446 106 452 82" fill="none" stroke="{ORANGE}" stroke-width="3.2" stroke-linecap="round"/>
<path class="thread t2" d="M416 236 C 444 262 446 304 452 330" fill="none" stroke="{ORANGE}" stroke-width="3.2" stroke-linecap="round"/>
<g class="match"><circle cx="452" cy="58" r="22" fill="{WHITE}" stroke="{INK}" stroke-width="{SW}"/><path d="M441 58 l7 7 l13 -14" fill="none" stroke="{ORANGE}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>
<g class="match m2"><circle cx="452" cy="352" r="22" fill="{WHITE}" stroke="{INK}" stroke-width="{SW}"/><path d="M441 352 l7 7 l13 -14" fill="none" stroke="{ORANGE}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>
</svg>
'''
(OUT / 'duo-animated.svg').write_text(duo)
print('wrote', sorted(p.name for p in OUT.iterdir()))
