# Fahem & Wasel — team design handoff

Prepared by Rigad · 6 November 2026.

This package brings together the Fahem & Wasel visual direction, original mascot icons, character explorations, motion studies and interactive frontend. The icons received particular attention: the selected pair is Fahem G and Wasel E, with distinct headwear, expressions and one accent colour each.

## Open the labs

From the repository root, run:

```sh
python3 -m http.server 8012 --bind 127.0.0.1
```

Start at **http://127.0.0.1:8012/design/fahem-wasel/**.

| Reference | What to review |
| --- | --- |
| [Design lab](../design/fahem-wasel/index.html) | Entry point for all design references and assets |
| [Brand kit](../design/fahem-wasel/brand-kit.html) | Identity, palette, type, voice, icon sizing and usage |
| [Motion lab](../fahem-wasel/motion-lab.html) | Agent moods, handoff, chat, matches, introductions, app shell and interview animations; use Replay and Reduce motion |
| [Character explorations](../design/fahem-wasel/iterations.html) | Earlier alternatives and the selected G/E pair |
| [Interactive frontend](../fahem-wasel/index.html) | Interview → profile review → match evidence → introduction → recipient preview |
| [Frontend guide](../fahem-wasel/README.md) | Sample journeys, reset and implementation limits |
| [Engineering plan](fahem-wasel-engineering-plan.md) | Proposed responsibilities, integration requirements and UX reference |
| [Earlier frontend QA](fahem-wasel-frontend-qa.md) | Observations from the original local browser review; separate from this handoff's checks |

The labs are static HTML/CSS/JavaScript; there is no compilation step or API key. Serve them over HTTP because the motion lab fetches the SVGs. Keep the `design/fahem-wasel/` and `fahem-wasel/` paths together. The brand kit requests Google Fonts; system fonts provide the fallback when offline.

## Mascots and visual direction

**Fahem / فاهم — the one who understands.** Blue `#2E4FC8`, Qatari cobra ghutra and agal, happy eyes, clean-shaven face. He listens, asks questions and helps turn a story into a profile.

**Wasel / واصل — the one who connects.** Orange `#D2591C`, embroidered Omani kumma, wink, clean-shaven face. He finds complementary people and guides introductions.

Use [fahem.svg](../design/fahem-wasel/fahem.svg) and [wasel.svg](../design/fahem-wasel/wasel.svg) for the current mascots, [mark.svg](../design/fahem-wasel/mark.svg) for the combined mark and [duo-animated.svg](../design/fahem-wasel/duo-animated.svg) for the animated handoff scene. The `*-portrait.svg` files are earlier detailed illustration studies, not the current selected icon pair.

The brand kit uses warm paper, ink, Instrument Serif, IBM Plex Sans / Arabic and Reem Kufi. The frontend and motion lab explore a quieter system-font app treatment. These are current reference surfaces; the team still needs to reconcile their tokens during integration.

## Editable sources

- `design/fahem-wasel/characters.py`: selected character geometry and semantic parts used by the icons and animation.
- `design/fahem-wasel/generate.py`: emits current icons, combined mark, duo scene and earlier portrait studies. Run `python3 design/fahem-wasel/generate.py design/fahem-wasel` from the repository root.
- `design/fahem-wasel/iterations.py`: earlier alternatives and comparison page. Regenerate with `python3 design/fahem-wasel/iterations.py`.
- `fahem-wasel/motion-lab.html`: self-contained motion studies with relative SVG fetches.
- `fahem-wasel/index.html`, `style.css`, `app.js`: frontend structure, styling and sample interactions.

## Integration handoff

Use the frontend to agree the visible journey and the motion lab to choose transitions. Motion-lab examples are proposals; their presence does not mean every animation is integrated into the app. Preserve meaningful feedback with reduced motion and validate it again after integration.

The frontend uses fictional profiles, scripted replies, simulated voice and local browser storage. It does not connect to the Handshake backend, perform live AI matching, record audio or deliver messages. Contact disclosure in this frontend is a demonstration; the backend must enforce the real consent boundary. Full Arabic/RTL remains to be built.

For the team walkthrough: open the design lab, compare the selected icons at small sizes, play the duo handoff, try motion-lab moods and replay controls, then walk through an interview and an introduction in the frontend. Agree which motion studies to ship before wiring the views to real services.

## Handoff verification — 6 November 2026

Served the packaged files locally and checked them in headless Chromium at 1440 px and 390 px widths. The design lab, brand kit, character explorations, frontend entry and motion lab loaded without browser errors, failed local requests, broken images or document horizontal overflow. Motion-lab SVG mounting, Reduce motion toggle, match-evidence expansion, interview answer/reset and all Replay buttons passed a smoke check. JavaScript syntax and Git whitespace checks passed. All six SVG outputs regenerated byte-for-byte from the supplied character sources.

These checks cover packaging and basic interactions; they do not certify every animation, physical-device behavior, complete frontend flows or backend integration. The earlier frontend QA report documents a separate, broader local walkthrough.
