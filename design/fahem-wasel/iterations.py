"""Three options each for Fahem (Qatari) and Wasel (Omani), as 64px line icons, plus a comparison page.
Run: python3 iterations.py   (writes iterations/*.svg and iterations.html next to this file)
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'iterations'; OUT.mkdir(exist_ok=True)
BLUE, ORANGE, WHITE, TILE = '#2E4FC8', '#D2591C', '#FFFFFF', '#F1EEE8'
LW = 1.8

def k(c):
    return f'fill="none" stroke="{c}" stroke-width="{LW}" stroke-linecap="round" stroke-linejoin="round"'

def shape(c, fill=WHITE):
    return f'fill="{fill}" stroke="{c}" stroke-width="{LW}" stroke-linejoin="round"'

# ---------------- Fahem: Qatari ----------------
COBRA_OUTER = 'M8 70 C 8 48 9.6 30.5 15 20.5 C 19.4 12.2 25.4 7.6 32 7.6 C 38.6 7.6 44.6 12.2 49 20.5 C 54.4 30.5 56 48 56 70 Z'
COBRA_INNER = 'M16.6 70 C 16.2 55 16.6 44 18.4 36.4 C 20.4 29.2 25.4 24.4 32 18.8 C 38.6 24.4 43.6 29.2 45.6 36.4 C 47.4 44 47.8 55 47.4 70 Z'

def fahem_head(c, beard='full', crest=False, glasses='round'):
    s = [f'<path fill-rule="evenodd" d="{COBRA_OUTER} {COBRA_INNER}" {shape(c)}/>']
    s.append(f'<path d="M18.6 15.8 C 24.2 12 39.8 12 45.4 15.8" {k(c)}/><path d="M16.8 19.8 C 23.4 15.8 40.6 15.8 47.2 19.8" {k(c)}/>')
    if crest:  # the raised front fold of the cobra, sitting on the cloth above the brow
        s.append(f'<path d="M23.2 23.6 C 26.6 20.4 29.4 17.6 32 13.4 C 34.6 17.6 37.4 20.4 40.8 23.6" {k(c)}/>')
    s.append(f'<path d="M23.6 31 Q 26.6 29.2 29.6 30.4 M34.4 30.4 Q 37.4 29.2 40.4 31" {k(c)}/>')
    if glasses == 'round':
        s.append(f'<g class="eyes"><circle cx="27" cy="35.8" r="3" {k(c)}/><circle cx="37" cy="35.8" r="3" {k(c)}/><path d="M30 35.4 Q 32 34.4 34 35.4" {k(c)}/>'
                 f'<circle cx="27" cy="36" r="1.5" fill="{c}"/><circle cx="37" cy="36" r="1.5" fill="{c}"/></g>')
    else:
        s.append(f'<g class="eyes"><rect x="23.4" y="33" width="7.4" height="5.6" rx="2.4" {k(c)}/><rect x="33.2" y="33" width="7.4" height="5.6" rx="2.4" {k(c)}/><path d="M30.8 35.4 Q 32 34.6 33.2 35.4" {k(c)}/>'
                 f'<circle cx="27.1" cy="36" r="1.45" fill="{c}"/><circle cx="36.9" cy="36" r="1.45" fill="{c}"/></g>')
    s.append(f'<path d="M32.2 39.4 C 31.4 41.2 31 42.4 32.6 43" {k(c)}/>')
    if beard == 'full':
        s.append(f'<path d="M18.8 41 C 19.4 53.5 25 61 32 61 C 39 61 44.6 53.5 45.2 41 C 43.6 44.8 40.4 46.2 37 46 C 35.4 44.6 28.6 44.6 27 46 C 23.6 46.2 20.4 44.8 18.8 41 Z" fill="{c}"/>'
                 f'<path d="M28.4 50.4 Q 32 53 35.6 50.4" fill="none" stroke="{WHITE}" stroke-width="{LW}" stroke-linecap="round"/>')
    else:  # moustache and goatee
        s.append(f'<path d="M26.8 45.6 C 29.2 43.8 34.8 43.8 37.2 45.6 C 34.8 46.9 29.2 46.9 26.8 45.6 Z" fill="{c}"/>'
                 f'<path d="M28.6 49.6 Q 32 51.8 35.4 49.6" {k(c)}/>'
                 f'<path d="M29.2 54.8 C 30.2 57.8 33.8 57.8 34.8 54.8 C 33.4 55.7 30.6 55.7 29.2 54.8 Z" fill="{c}"/>')
    return ''.join(s)

def fahem_a(c=BLUE): return fahem_head(c, beard='full')
def fahem_b(c=BLUE): return fahem_head(c, beard='goatee', crest=True, glasses='square')
def fahem_c(c=BLUE):
    bisht = (f'<path d="M1 70 C 3 56 13 50.4 23.6 48.6 L 32 60 L 40.4 48.6 C 51 50.4 61 56 63 70 Z" {shape(c)}/>'
             f'<path d="M23.6 48.6 C 25.4 54.6 28.4 58.4 32 60 C 35.6 58.4 38.6 54.6 40.4 48.6 M20.6 49.4 C 22.8 56.6 26.8 61.6 32 63.4 C 37.2 61.6 41.2 56.6 43.4 49.4" {k(c)}/>')
    return bisht + f'<g transform="translate(7.2 -2.6) scale(0.775)">{fahem_head(c, beard="full")}</g>'

# ---------------- Wasel: Omani ----------------
def wasel_face(c, top=30, beard=True):
    return (f'<path d="M18 {top+3.4} C 14.4 {top+2.8} 14 {top+10.8} 18.2 {top+11} M46 {top+3.4} C 49.6 {top+2.8} 50 {top+10.8} 45.8 {top+11}" {k(c)}/>'
            f'<path d="M18.2 {top} C 17.6 42 19.6 51.6 25 56.6 C 28.6 60 35.4 60 39 56.6 C 44.4 51.6 46.4 42 45.8 {top}" {shape(c, TILE)}/>'
            f'<path d="M35.6 33.4 Q 38.4 31.8 41 33 M23.4 33.8 Q 26.2 32.8 29 33.6" {k(c)}/>'
            f'<g class="eyes"><path d="M24.4 37.4 Q 27 39.4 29.6 37.4" {k(c)}/><circle cx="38.2" cy="37.6" r="1.6" fill="{c}"/></g>'
            f'<path d="M32.4 39.8 C 34.2 41.8 34.2 43.8 31.6 44.8" {k(c)}/>'
            + (f'<path d="M19.6 44.4 C 20.4 52.8 25.4 58.6 32 58.6 C 38.6 58.6 43.6 52.8 44.4 44.4 C 42.4 47.8 39.6 49.2 36.6 49 C 35 47.8 29 47.8 27.4 49 C 24.4 49.2 21.6 47.8 19.6 44.4 Z" fill="{c}"/>'
               f'<path d="M27.6 51.2 C 28.8 54.6 35.2 54.6 36.4 51.2 Z" fill="{WHITE}"/>' if beard else
               f'<path d="M27.2 49.4 C 28.6 54.2 35.4 54.2 36.8 49.4 Z" fill="{WHITE}" stroke="{c}" stroke-width="{LW}" stroke-linejoin="round"/>'))

def kumma(c):
    dots = ''.join(f'<circle cx="{x}" cy="20.8" r="0.85" fill="{c}"/>' for x in (21.4, 25.6, 29.8, 34.2, 38.4, 42.6))
    rings = ''.join(f'<circle cx="{x}" cy="24" r="1" fill="none" stroke="{c}" stroke-width="1.1"/>' for x in (23.5, 28.6, 35.4, 40.5))
    return (f'<path d="M17.2 30.4 C 16.6 23 17.2 17.4 19.6 14.4 C 25.6 11.4 38.4 11.4 44.4 14.4 C 46.8 17.4 47.4 23 46.8 30.4 C 38.8 28.6 25.2 28.6 17.2 30.4 Z" {shape(c)}/>'
            f'<path d="M19.6 14.4 C 25.6 16.6 38.4 16.6 44.4 14.4" {k(c)}/>{dots}{rings}')

def wasel_a(c=ORANGE): return wasel_face(c) + kumma(c)

def wasel_b(c=ORANGE):
    massar = (f'<path d="M12.4 31.4 C 10.2 21.6 13.6 11.4 22.4 8.2 C 27.6 6.2 36.4 6.2 41.6 8.2 C 50.4 11.4 53.8 21.6 51.6 31.4 C 44.8 28.6 38.4 27.6 32 27.6 C 25.6 27.6 19.2 28.6 12.4 31.4 Z" {shape(c)}/>'
              f'<path d="M13.4 25.8 C 21.2 22 42.8 22 50.6 25.8 M14.8 18.6 C 22.4 14.8 41.6 14.8 49.2 18.6 M20.4 11.6 C 26 9.6 38 9.6 43.6 11.6" {k(c)}/>'
              + ''.join(f'<path d="M{x} 21.6 c 1.4 -0.2 2 1.4 0.8 2.2 c -1 0.6 -2 -0.4 -0.8 -2.2 Z" fill="{c}"/>' for x in (20.6, 27.4, 34.2, 41)) +
              f'<path d="M50.8 25 C 54.4 28 55.6 32 55.2 37" {k(c)}/><path d="M53.4 36.6 V 39.6 M55.2 37 V 40 M56.8 36.2 V 38.8" {k(c)}/>')
    return wasel_face(c, top=30.4) + massar

def wasel_c(c=ORANGE):
    body = (f'<path d="M2 70 C 4 57 14 51 25 50 C 28.4 53 35.6 53 39 50 C 50 51 60 57 62 70 Z" {shape(c)}/>'
            f'<path d="M32 52.8 V 58.4" {k(c)}/><path d="M32 58.2 C 30.4 59.6 30.4 62.8 32 64 C 33.6 62.8 33.6 59.6 32 58.2 Z" fill="{c}"/>'
            f'<path d="M30.8 64.2 l -0.6 2.2 M32 64.6 v 2.4 M33.2 64.2 l 0.6 2.2" {k(c)}/>')
    return body + f'<g transform="translate(7.2 -3.2) scale(0.775)">{wasel_face(c) + kumma(c)}</g>'

# ---------------- Fahem, round two: same construction as Wasel C (a real face, a bust), Qatari details ----------------
def fahem_friendly(c, eyes='happy', glasses=False, beard='boxed'):
    ghutra_back = f'<path d="M7 80 C 8.6 56 10.6 34 15.4 22 C 19.4 12.8 25.4 8 32 8 C 38.6 8 44.6 12.8 48.6 22 C 53.4 34 55.4 56 57 80 Z" {shape(c)}/>'
    face = (f'<path d="M18.2 30 C 17.6 42 19.6 51.6 25 56.6 C 28.6 60 35.4 60 39 56.6 C 44.4 51.6 46.4 42 45.8 30 '
            f'C 45.8 24 39 19.6 32 19.6 C 25 19.6 18.2 24 18.2 30 Z" {shape(c, TILE)}/>')
    # the cloth over the forehead: its lower edge rises to the cobra point at the hairline
    cover = (f'<path d="M16.6 31.6 C 19.4 27 26.4 25 32 21.4 C 37.6 25 44.6 27 47.4 31.6 L 48 22 C 44.4 13.8 38.2 10.8 32 10.8 C 25.8 10.8 19.6 13.8 16 22 Z" fill="{WHITE}"/>'
             f'<path d="M16.6 31.6 C 19.4 27 26.4 25 32 21.4 C 37.6 25 44.6 27 47.4 31.6" {k(c)}/>')
    agal = f'<path d="M19.2 15.6 C 24.8 11.8 39.2 11.8 44.8 15.6" {k(c)}/><path d="M17.6 19.6 C 24 15.6 40 15.6 46.4 19.6" {k(c)}/>'
    brows = f'<path d="M23.4 31.4 Q 26.2 30 29 30.8 M35 30.8 Q 37.8 30 40.6 31.4" {k(c)}/>'
    if glasses:
        eyes_svg = (f'<g class="eyes"><circle cx="26.8" cy="36" r="2.9" {k(c)}/><circle cx="37.2" cy="36" r="2.9" {k(c)}/><path d="M29.7 35.6 Q 32 34.6 34.3 35.6" {k(c)}/>'
                    f'<circle cx="26.8" cy="36.2" r="1.45" fill="{c}"/><circle cx="37.2" cy="36.2" r="1.45" fill="{c}"/></g>')
    elif eyes == 'happy':
        eyes_svg = f'<g class="eyes"><path d="M24.2 36.6 Q 26.8 34 29.4 36.6 M34.6 36.6 Q 37.2 34 39.8 36.6" {k(c)}/></g>'
    else:
        eyes_svg = f'<g class="eyes"><circle cx="26.8" cy="36" r="1.6" fill="{c}"/><circle cx="37.2" cy="36" r="1.6" fill="{c}"/></g>'
    nose = f'<path d="M32.4 38.8 C 34 40.8 33.8 42.8 31.6 43.6" {k(c)}/>'
    if beard is None:
        beard_svg = ''
    elif beard == 'mustache':
        beard_svg = f'<path d="M26.8 46 C 29.2 44.2 34.8 44.2 37.2 46 C 34.8 47.3 29.2 47.3 26.8 46 Z" fill="{c}"/>'
    elif beard == 'full':
        beard_svg = (f'<path d="M18.6 42.6 C 19.4 54 25 61.4 32 61.4 C 39 61.4 44.6 54 45.4 42.6 C 43.4 46.8 40.2 48.6 36.8 48.4 C 35.2 47.2 28.8 47.2 27.2 48.4 C 23.8 48.6 20.6 46.8 18.6 42.6 Z" fill="{c}"/>')
    else:
        beard_svg = (f'<path d="M19.6 44.4 C 20.4 52.8 25.4 58.6 32 58.6 C 38.6 58.6 43.6 52.8 44.4 44.4 C 42.4 47.8 39.6 49.2 36.6 49 C 35 47.8 29 47.8 27.4 49 C 24.4 49.2 21.6 47.8 19.6 44.4 Z" fill="{c}"/>')
    smile = (f'<path d="M28.2 51.6 Q 32 54.6 35.8 51.6" fill="none" stroke="{WHITE}" stroke-width="{LW}" stroke-linecap="round"/>' if beard in ('boxed', 'full')
             else f'<path d="M27.6 50.2 Q 32 54 36.4 50.2" {k(c)}/>')
    return ghutra_back + face + cover + agal + brows + eyes_svg + nose + beard_svg + smile

def qatari_bust(c, **kw):
    body = (f'<path d="M2 70 C 4 57 14 51 25 50 C 28.4 53 35.6 53 39 50 C 50 51 60 57 62 70 Z" {shape(c)}/>'
            f'<path d="M25.4 50.4 L 28.6 56.4 L 32 53.6 L 35.4 56.4 L 38.6 50.4" {shape(c)}/>'
            f'<circle cx="32" cy="59.4" r="0.85" fill="{c}"/><circle cx="32" cy="63.6" r="0.85" fill="{c}"/>')
    return f'<g transform="translate(7.2 -3.2) scale(0.775)">{fahem_friendly(c, **kw)}</g>' + body

def fahem_d(c=BLUE): return qatari_bust(c, eyes='happy')
def fahem_e(c=BLUE): return qatari_bust(c, glasses=True)
def fahem_f(c=BLUE): return qatari_bust(c, glasses=True, beard='full')

# ---------------- Round three: heads only ----------------
def fahem_g(c=BLUE): return fahem_friendly(c, eyes='happy', beard=None)
def fahem_h(c=BLUE): return fahem_friendly(c, eyes='happy', beard='mustache')
def wasel_d(c=ORANGE): return wasel_face(c) + kumma(c)
def wasel_e(c=ORANGE): return wasel_face(c, beard=False) + kumma(c)

def tile(inner, name):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="{name}">'
            f'<defs><clipPath id="clip-{name}"><rect width="64" height="64" rx="14"/></clipPath></defs>'
            f'<rect width="64" height="64" rx="14" fill="{TILE}"/><g clip-path="url(#clip-{name})">{inner}</g></svg>\n')

OPTIONS = [
    ('fahem-a', fahem_a(), 'Fahem A', 'Cobra ghutra, agal, round glasses, full beard.'),
    ('fahem-b', fahem_b(), 'Fahem B', 'Raised cobra crest on the cloth, square glasses, moustache and goatee.'),
    ('fahem-c', fahem_c(), 'Fahem C', 'Formal bust: cobra ghutra over a bisht with its trim, full beard.'),
    ('wasel-a', wasel_a(), 'Wasel A', 'Embroidered Omani kumma cap, wink, boxed beard.'),
    ('wasel-b', wasel_b(), 'Wasel B', 'Full rounded massar: curved wraps, paisley embroidery, fringed end.'),
    ('wasel-c', wasel_c(), 'Wasel C', 'Kumma cap plus the furakha tassel on the dishdasha collar.'),
    ('fahem-d', fahem_d(), 'Fahem D', 'Same build as Wasel C: real face, cobra ghutra behind it, happy eyes, short beard.'),
    ('fahem-e', fahem_e(), 'Fahem E', 'Small round glasses, open eyes, soft smile, short beard.'),
    ('fahem-f', fahem_f(), 'Fahem F', 'The older, wise one: small glasses and a fuller beard.'),
    ('fahem-g', fahem_g(), 'Fahem G', 'Fahem D as a head only: happy eyes, clean-shaven.'),
    ('fahem-h', fahem_h(), 'Fahem H', 'Fahem D as a head only: happy eyes, moustache.'),
    ('wasel-d', wasel_d(), 'Wasel D', 'Wasel C as a head only: kumma, wink, beard.'),
    ('wasel-e', wasel_e(), 'Wasel E', 'Wasel C as a head only: kumma, wink, clean-shaven.'),
]
for slug, inner, title, _ in OPTIONS:
    (OUT / f'{slug}.svg').write_text(tile(inner, slug))

cards = lambda prefix: ''.join(
    f'<figure><img src="iterations/{slug}.svg" width="168" alt="{title}"><div class="small"><img src="iterations/{slug}.svg" width="40" alt=""><img src="iterations/{slug}.svg" width="28" alt=""></div>'
    f'<figcaption><b>{title}</b>{note}</figcaption></figure>' for slug, _, title, note in OPTIONS if slug.startswith(prefix))
(HERE / 'iterations.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fahem &amp; Wasel — options</title>
<style>
body{{margin:0;background:#FBF8F3;color:#1B1B1F;font:400 15px/1.5 'IBM Plex Sans',system-ui,sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:40px 24px 64px}}
h1{{font:400 34px Georgia,serif;margin:0 0 6px}} h2{{font:400 24px Georgia,serif;margin:36px 0 14px}}
p.lead{{color:#55524E;margin:0}}
.row{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}
figure{{margin:0;padding:20px;border-radius:22px;background:#fff;border:1px solid #E6E1D8;display:flex;flex-direction:column;align-items:center;gap:12px}}
.small{{display:flex;gap:12px;align-items:flex-end}} .pair{{display:flex;gap:10px}}
figcaption{{text-align:center;font-size:14px;color:#55524E}} figcaption b{{display:block;font-size:16px;color:#1B1B1F}}
@media(max-width:760px){{.row{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Fahem &amp; Wasel: pick one of each</h1>
<p class="lead">Fahem is Qatari (blue). Wasel is Omani (orange). Each is shown at 168, 40 and 28 px.</p>
<h2>Round three · heads only</h2><div class="row">{''.join(f'<figure><div class="pair"><img src="iterations/{a}.svg" width="150" alt=""><img src="iterations/{b}.svg" width="150" alt=""></div><div class="small"><img src="iterations/{a}.svg" width="40" alt=""><img src="iterations/{b}.svg" width="40" alt=""><img src="iterations/{a}.svg" width="28" alt=""><img src="iterations/{b}.svg" width="28" alt=""></div><figcaption><b>{label}</b>{note}</figcaption></figure>' for a,b,label,note in (('fahem-g','wasel-e','Fahem G + Wasel E','Both clean-shaven.'),('fahem-g','wasel-d','Fahem G + Wasel D','Fahem clean-shaven, Wasel bearded.'),('fahem-h','wasel-d','Fahem H + Wasel D','Fahem with a moustache, Wasel bearded.')))}</div>
<h2>Round two · Fahem next to Wasel C</h2><div class="row">{''.join(f'<figure><div class="pair"><img src="iterations/{x}.svg" width="150" alt=""><img src="iterations/wasel-c.svg" width="150" alt=""></div><div class="small"><img src="iterations/{x}.svg" width="40" alt=""><img src="iterations/wasel-c.svg" width="40" alt=""><img src="iterations/{x}.svg" width="28" alt=""><img src="iterations/wasel-c.svg" width="28" alt=""></div><figcaption><b>{t} + Wasel C</b>{n}</figcaption></figure>' for x,_,t,n in OPTIONS if x in ('fahem-d','fahem-e','fahem-f'))}</div>
<h2>Round one · Fahem</h2><div class="row">{cards('fahem-a')}{cards('fahem-b')}{cards('fahem-c')}</div>
<h2>Wasel · Oman</h2><div class="row">{cards('wasel')}</div>
</main></body></html>
''')
print('wrote', sorted(p.name for p in OUT.iterdir()), 'and iterations.html')
