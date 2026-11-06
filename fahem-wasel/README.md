# Fahem & Wasel frontend

A standalone, sample-data UX prototype inspired by the Jack & Jill candidate dashboard. This is separate from the older Karak and Handshake prototypes; their files and storage are unchanged.

From the repository root:

```sh
python3 -m http.server 8012 --bind 127.0.0.1
```

Open http://127.0.0.1:8012/fahem-wasel/ . No build, dependencies or API keys are needed. You can also open `index.html` directly; using a local server is preferable for consistent browser storage.

## Try these journeys

- **Find someone:** expand “Why you two,” view a full profile, save or pass, then undo a pass.
- **Introduce yourself:** request Lina’s introduction, edit the note, then open Introductions → Sent → Preview recipient. Accept to see the connected state and sample contact. Try declining or withdrawing another request.
- **Tell your story:** Talk to Fahem → Talk to Fahem. Answer the seven questions or use sample answers. Review/edit the profile, confirm it, and find matches.
- **Shape the search:** choose “In person” in preferences and save. The list narrows to three Doha profiles. Search for a missing name to see the empty state.
- **Voice preview:** the microphone or conversation menu opens a simulated conversation with waveform, pause/resume, timer and an editable sample transcript. No microphone is accessed.
- **Your notes:** review the seven interview answers, download notes, add a sample CV, or select a local document to preview its file name. No document is uploaded or analyzed.
- **Reset:** account menu → Reset sample data. State is stored under `fahem-wasel-ux-v1` in localStorage. Settings also includes reduced motion and a demo-data download.

## What is simulated

Five fictional candidate profiles, two incoming requests, scripted agent replies, progress steps and recipient acceptance. Sample contacts use `example.com`. Only work arrangement and start-date preferences filter the sample list. Remaining preference fields are saved but do not run semantic matching. There is no AI, real message delivery, identity verification, backend, secure contact storage or audio recording.

The frontend contact gate is an interaction demonstration, not a security boundary. A real service must enforce authorization and contact disclosure server-side.

## Files

- `index.html`: entry point.
- `style.css`: layout, visual tokens, responsive behavior and motion.
- `app.js`: fixtures, local state, views and interactions.
- `../design/fahem-wasel/`: existing brand marks and agent illustrations.

The interface is English. Full Arabic translation and RTL layout have not been implemented.

## Design and motion references

Start with the [design lab](../design/fahem-wasel/index.html), [motion lab](motion-lab.html) and [team handoff](../docs/fahem-wasel-handoff.md). The motion lab needs the local HTTP server above to load its SVG assets. Its animation studies are proposals rather than a list of effects already integrated into this frontend.
