# Fahem & Wasel frontend: browser review

6 November 2026. Reviewed against the served app at `/fahem-wasel/` using the in-app browser. This is a local sample-data prototype, not a deployed or connected product.

## Observed working

- Initial match list, expandable complementary-fit evidence and candidate details.
- Save toggle and count; pass and bring-back recovery; empty category state.
- Search with a no-result state and clear-search recovery.
- Editable introduction note, sample request, pending state, recipient preview and acceptance.
- A sample contact link appears in Connected after acceptance.
- Received request decline and sent request withdrawal both reach Closed, with no contact links in that view.
- Profile headline edit, changed-value Save, confirmation required after editing, and re-confirmation.
- All seven interview questions using sample answers, profile review and confirmation, then simulated matching progress to results.
- In-person preference reduces the five sample matches to three Doha profiles.
- Interview notes contain all seven question/answer pairs. Adding the sample CV creates a document entry.
- Voice preview opens with sample transcript, pause/resume control, timer and use-transcript action.
- Saved introduction state survives reload.
- Reduce-motion control updates its checked state.
- Reset restores the original five matches, profile and incoming requests.
- Layouts reviewed at 1003 × 1194, 390 × 844, 360 × 800 and 1440 × 900. No document horizontal overflow was observed at mobile sizes. At 390 × 844, the composer bottom was 756 px and mobile navigation began at 787 px.
- Profile, preferences and introduction screens had no horizontal overflow at 390 px. A request modal fit inside a 360 px viewport.
- Modal background is marked inert; keyboard focus is constrained by the dialog handler. The unchanged profile Save button is disabled.
- JavaScript syntax check passed; no browser error entries were observed during the reviewed flows.

## Adjustments made during review

- Profile confirmation state and onboarding completion now follow user actions.
- The divider can resize chat at desktop breakpoints; motion respects both the system setting and the app preference.
- Collapsed evidence regions are inert, and dialog focus does not scroll the background to the invoking button.
- The sample carousel uses the same location, availability and pass exclusions as the suggestion list.
- The search summary describes the actual five-profile sample batch.
- Mobile account navigation exposes the interview and document screens.

## Limits

Speech, AI replies, matching progress, recipient identity and messages are simulated. Full Arabic/RTL, actual file parsing, real account authentication, durable server storage, backend authorization, physical-device testing, and exhaustive keyboard/screen-reader auditing remain outside this frontend build. Download controls and real-file selection are implemented but were not verified by downloading or selecting a personal file in this review. The pointer-drag divider was implemented but not physically dragged during this review.
