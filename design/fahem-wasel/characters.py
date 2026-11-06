"""The final Fahem (Qatari) and Wasel (Omani) drawings: the single source for the icons, the animation and the brand kit.
Chosen from iterations.html: Fahem G (cobra ghutra, happy eyes, clean-shaven) and Wasel E (embroidered kumma, wink, clean-shaven).
"""
BLUE, ORANGE, WHITE, TILE = '#2E4FC8', '#D2591C', '#FFFFFF', '#F1EEE8'
LW = 1.8

def k(c):
    return f'fill="none" stroke="{c}" stroke-width="{LW}" stroke-linecap="round" stroke-linejoin="round"'

def shape(c, fill=WHITE):
    return f'fill="{fill}" stroke="{c}" stroke-width="{LW}" stroke-linejoin="round"'

def fahem_friendly(c, eyes='happy', glasses=False, beard='boxed', bg=TILE):
    ghutra_back = f'<path class="ghutra" d="M7 80 C 8.6 56 10.6 34 15.4 22 C 19.4 12.8 25.4 8 32 8 C 38.6 8 44.6 12.8 48.6 22 C 53.4 34 55.4 56 57 80 Z" {shape(c)}/>'
    face = (f'<path d="M18.2 30 C 17.6 42 19.6 51.6 25 56.6 C 28.6 60 35.4 60 39 56.6 C 44.4 51.6 46.4 42 45.8 30 '
            f'C 45.8 24 39 19.6 32 19.6 C 25 19.6 18.2 24 18.2 30 Z" {shape(c, bg)}/>')
    # the cloth over the forehead: its lower edge rises to the cobra point at the hairline
    cover = (f'<path d="M16.6 31.6 C 19.4 27 26.4 25 32 21.4 C 37.6 25 44.6 27 47.4 31.6 L 48 22 C 44.4 13.8 38.2 10.8 32 10.8 C 25.8 10.8 19.6 13.8 16 22 Z" fill="{WHITE}"/>'
             f'<path d="M16.6 31.6 C 19.4 27 26.4 25 32 21.4 C 37.6 25 44.6 27 47.4 31.6" {k(c)}/>')
    agal = f'<path d="M19.2 15.6 C 24.8 11.8 39.2 11.8 44.8 15.6" {k(c)}/><path d="M17.6 19.6 C 24 15.6 40 15.6 46.4 19.6" {k(c)}/>'
    brows = f'<path class="brows" d="M23.4 31.4 Q 26.2 30 29 30.8 M35 30.8 Q 37.8 30 40.6 31.4" {k(c)}/>'
    if glasses:
        eyes_svg = (f'<g class="eyes"><circle cx="26.8" cy="36" r="2.9" {k(c)}/><circle cx="37.2" cy="36" r="2.9" {k(c)}/><path d="M29.7 35.6 Q 32 34.6 34.3 35.6" {k(c)}/>'
                    f'<circle cx="26.8" cy="36.2" r="1.45" fill="{c}"/><circle cx="37.2" cy="36.2" r="1.45" fill="{c}"/></g>')
    elif eyes == 'happy':
        eyes_svg = f'<g class="eyes"><path d="M24.2 36.6 Q 26.8 34 29.4 36.6 M34.6 36.6 Q 37.2 34 39.8 36.6" {k(c)}/></g>'
    else:
        eyes_svg = f'<g class="eyes"><circle cx="26.8" cy="36" r="1.6" fill="{c}"/><circle cx="37.2" cy="36" r="1.6" fill="{c}"/></g>'
    nose = f'<path class="nose" d="M32.4 38.8 C 34 40.8 33.8 42.8 31.6 43.6" {k(c)}/>'
    if beard is None:
        beard_svg = ''
    elif beard == 'mustache':
        beard_svg = f'<path d="M26.8 46 C 29.2 44.2 34.8 44.2 37.2 46 C 34.8 47.3 29.2 47.3 26.8 46 Z" fill="{c}"/>'
    elif beard == 'full':
        beard_svg = (f'<path d="M18.6 42.6 C 19.4 54 25 61.4 32 61.4 C 39 61.4 44.6 54 45.4 42.6 C 43.4 46.8 40.2 48.6 36.8 48.4 C 35.2 47.2 28.8 47.2 27.2 48.4 C 23.8 48.6 20.6 46.8 18.6 42.6 Z" fill="{c}"/>')
    else:
        beard_svg = (f'<path d="M19.6 44.4 C 20.4 52.8 25.4 58.6 32 58.6 C 38.6 58.6 43.6 52.8 44.4 44.4 C 42.4 47.8 39.6 49.2 36.6 49 C 35 47.8 29 47.8 27.4 49 C 24.4 49.2 21.6 47.8 19.6 44.4 Z" fill="{c}"/>')
    smile = (f'<path d="M28.2 51.6 Q 32 54.6 35.8 51.6" fill="none" stroke="{WHITE}" stroke-width="{LW}" stroke-linecap="round"/>' if beard in ('boxed', 'full')
             else f'<path class="mouth" d="M27.6 50.2 Q 32 54 36.4 50.2" {k(c)}/>')
    return ghutra_back + face + f'<g class="headwear">{cover}{agal}</g>' + brows + eyes_svg + nose + beard_svg + smile

def wasel_face(c, top=30, beard=True, bg=TILE):
    return (f'<path class="ears" d="M18 {top+3.4} C 14.4 {top+2.8} 14 {top+10.8} 18.2 {top+11} M46 {top+3.4} C 49.6 {top+2.8} 50 {top+10.8} 45.8 {top+11}" {k(c)}/>'
            f'<path d="M18.2 {top} C 17.6 42 19.6 51.6 25 56.6 C 28.6 60 35.4 60 39 56.6 C 44.4 51.6 46.4 42 45.8 {top}" {shape(c, bg)}/>'
            f'<path class="brows" d="M35.6 33.4 Q 38.4 31.8 41 33 M23.4 33.8 Q 26.2 32.8 29 33.6" {k(c)}/>'
            f'<g class="eyes"><path d="M24.4 37.4 Q 27 39.4 29.6 37.4" {k(c)}/><circle class="pupil" cx="38.2" cy="37.6" r="1.6" fill="{c}"/></g>'
            f'<path d="M32.4 39.8 C 34.2 41.8 34.2 43.8 31.6 44.8" {k(c)}/>'
            + (f'<path d="M19.6 44.4 C 20.4 52.8 25.4 58.6 32 58.6 C 38.6 58.6 43.6 52.8 44.4 44.4 C 42.4 47.8 39.6 49.2 36.6 49 C 35 47.8 29 47.8 27.4 49 C 24.4 49.2 21.6 47.8 19.6 44.4 Z" fill="{c}"/>'
               f'<path class="mouth" d="M27.6 51.2 C 28.8 54.6 35.2 54.6 36.4 51.2 Z" fill="{WHITE}"/>' if beard else
               f'<path class="mouth" d="M27.2 49.4 C 28.6 54.2 35.4 54.2 36.8 49.4 Z" fill="{WHITE}" stroke="{c}" stroke-width="{LW}" stroke-linejoin="round"/>'))

def kumma(c):
    dots = ''.join(f'<circle class="stitch" cx="{x}" cy="20.8" r="0.85" fill="{c}"/>' for x in (21.4, 25.6, 29.8, 34.2, 38.4, 42.6))
    rings = ''.join(f'<circle cx="{x}" cy="24" r="1" fill="none" stroke="{c}" stroke-width="1.1"/>' for x in (23.5, 28.6, 35.4, 40.5))
    return '<g class="headwear">' + (f'<path d="M17.2 30.4 C 16.6 23 17.2 17.4 19.6 14.4 C 25.6 11.4 38.4 11.4 44.4 14.4 C 46.8 17.4 47.4 23 46.8 30.4 C 38.8 28.6 25.2 28.6 17.2 30.4 Z" {shape(c)}/>'
            f'<path d="M19.6 14.4 C 25.6 16.6 38.4 16.6 44.4 14.4" {k(c)}/>{dots}{rings}') + '</g>'


def fahem_icon(c=BLUE, prefix='', bg=TILE):
    """Fahem, from Qatar: white cobra ghutra and agal, happy eyes, a warm smile."""
    inner = fahem_friendly(c, eyes='happy', beard=None, bg=bg).replace('class="eyes"', f'class="{prefix}eyes"')
    return f'<g class="{prefix}face">{inner}</g>'


def wasel_icon(c=ORANGE, prefix='', bg=TILE):
    """Wasel, from Oman: the embroidered kumma cap, a wink, an open smile."""
    inner = (wasel_face(c, beard=False, bg=bg) + kumma(c)).replace('class="eyes"', f'class="{prefix}eyes"')
    return f'<g class="{prefix}face">{inner}</g>'
