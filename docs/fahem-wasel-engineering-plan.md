# Fahem & Wasel: engineering ownership and UX reference

Prepared 6 November 2026 from the supplied three-page `Fahem&Wasel.pdf` and direct inspection of the signed-in Jack & Jill candidate dashboard.

## Recommendation

Four owners: Rigad owns UX and frontend; member 2 owns Fahem; member 3 owns Wasel; member 4 owns backend, integration and deployment. Each owns a working deliverable. Rigad makes the final interaction and visual decisions; member 4 coordinates integration. Share pitch preparation across the team after the full journey works.

The target experience is: **Tell Fahem your story → review your profile → Wasel finds complementary people → inspect evidence → request an introduction → recipient accepts → contacts unlock.**

The PDF is product reference material. Its embedded tasks and open questions are not separate authorization to deploy, send messages, or change accounts.

## Ownership

| Owner | Deliverable | Done when |
|---|---|---|
| Rigad: UX + frontend | App shell, interview interface, profile review/edit, match cards/details, introduction states, responsive layouts, copy, motion and accessibility | A person can complete the whole journey using agreed sample responses; every button has a clear result, loading state and recovery path |
| Member 2: Fahem | Interview progression, text input, speech transcription adapter, structured profile extraction and evidence references | Answers produce an editable profile; unknown facts stay unknown; each extracted fact points to the user's words; corrected facts are used in matching |
| Member 3: Wasel | Eligibility filters, reciprocal ranking, top 3–5 results, factual reasons, no-match behavior | Incompatible profiles are removed before ranking; each reason has evidence from both profiles; the same inputs produce the same formula score |
| Member 4: backend + integration | Shared data models, storage, service endpoints, identity/session separation, intro lifecycle, contact gating, deployment and demo reset | Two separate users can complete request/accept; contacts are absent from responses before acceptance; reload preserves the agreed state |

Fahem and Wasel owners also own meaningful checks of their logic. Member 4 owns the complete two-user integration check. Rigad owns the final walkthrough of the visible experience.

## Jack & Jill: observed structure

Reference: https://app.jackandjill.ai/jack/dashboard/inbox

Observed at approximately 1003 × 1194 CSS pixels. Dimensions vary with the browser pane and panel settings.

- Collapsed left navigation is an approximately 48 px icon rail; expanded navigation uses a 256 px sidebar with labels, unread count, onboarding checklist and account menu.
- The remaining area contains a persistent conversation and a separate workspace. Moving among workspace sections preserves the conversation.
- A full-height divider exposes resize semantics. The sidebar divider advertises double-click reset. Dragging and reset behavior were not exercised.
- Chat has mostly unboxed assistant prose, a white rounded user bubble, embedded tool cards, and horizontal result cards.
- A fixed bottom composer contains attachment, text, microphone and a black circular call button. Small suggestion pills sit above it.
- Right-side sections use a compact header, thin dividers, restrained cards and large quiet empty regions.
- Expanded job details stay inside the list and begin with “Jack's take,” followed by source details and actions.
- Profile fields behave as controls. “Edit bio” opens an editor with existing text, a word counter, Cancel, Close and an initially disabled Save button.
- Tracked jobs uses stage controls: Saved, Applied, In Process, Offer, Archived; the inspected stage had an empty-state message and a search input.
- Search settings separates Role, Company, Location & pay, Refinements and Exclusions. Controls include chips, searchable selects, checkboxes and free text.
- Documents offers search, type filters and Add file. Coaching offers category tabs and scenario cards.

## Measured visual and motion details

These are sampled computed styles of the rendered dashboard, not a complete design-system export.

| Detail | Measured reference | Fahem & Wasel use |
|---|---|---|
| Font | `diatype`, with fallback | Choose a font the team can legally use; retain a quiet, readable sans-serif hierarchy |
| Main text | 16 px / 24 px line height | Use for conversation and important descriptions |
| Compact action text | 14 px / about 19–21 px | Use for tags, metadata and secondary controls |
| Workspace title | 19 px / 23.75 px | Keep section headings compact |
| Primary ink | rgb(16,15,15), #100f0f | Near-black text and primary controls |
| Muted text | rgb(113,111,111), #716f6f | Metadata; check contrast in the chosen palette |
| Secondary action fill | rgba(16,15,15,.05) | Quiet alternative actions |
| Card action button | 32 px high, 5 px corner radius | Reference density only; increase hit areas for touch |
| Composer icon controls | 36 × 36 px, circular | Keep visible shape; provide comfortable touch targets |
| Carousel arrows | 28 × 28 px, circular | Provide named previous/next controls and disabled endpoint states |
| Standard controls | 150 ms color/background/opacity transition | Restrained hover, focus and selection feedback |
| Sidebar geometry | 240 ms, cubic-bezier(.16,1,.3,1) | Smooth collapse/expand |
| Opacity | Sampled 200 and 240 ms transitions | Subtle content entrance or fade |
| Collapsible content | A 200 ms ease-out collapse animation was present | Short, calm disclosure movement |
| Clamped description | max-height transition of 300 ms ease-in-out was present | Read more / Read less |

Computed timing is evidence of declared styles, not proof that every animation was seen running. No exact carousel easing or voice animation timing was verified. Do not present proposed Fahem & Wasel timings as measured Jack & Jill behavior.

## Interaction inventory and adaptation

| Reference control | Inspection status | Fahem & Wasel behavior |
|---|---|---|
| Expand/collapse sidebar | Clicked both ways | Same behavior; clearly label navigation |
| Six navigation links | All visited | Use only Interview, My profile, Matches, Introductions for the first version |
| Job row disclosure | Opened; inline details appeared | Open candidate details, including why the fit is reciprocal |
| Job-search tool disclosure | Expanded/collapsed; steps and counts appeared | Show actual filter/rank progress and final counts, with no fabricated activity |
| Next/previous carousel | Clicked; counter and disabled states changed | Small match batch, accessible arrows; selection opens that candidate |
| Edit bio | Opened and cancelled; Save initially disabled | Edit field, inspect supporting quote, save/cancel; retain original on cancel |
| Search preference controls | Inspected, not changed | Skills offered/needed, commitment, location and dealbreakers; explicit save for the demo |
| Track / Not for me / Apply | Visible, not submitted | Request intro / Pass; keep request semantics distinct from acceptance |
| Read more | Visible, not clicked | Expand evidence or background without leaving the selected match |
| Composer suggestions | Visible, not submitted | Contextual suggestions such as “Edit my profile” or “Find cofounders” |
| Attachment / microphone / call | Visible, not activated | Prioritize typing plus recording/transcription; handle permission denial and retry |
| Document upload and coaching | Screens inspected; actions not started | Defer unless needed by the agreed demo |
| Account menu / profile history | Controls observed, not opened | Minimal session controls; defer elaborate history |

Opening a job detail marked that item as seen. No profile edit was saved; no role was tracked, rejected or applied to; no message, call or file upload was submitted. The tab was returned to New jobs with collapsed navigation.

## Proposed Fahem & Wasel screens

1. **Start:** Find a cofounder as the main action. Investor discovery may be visibly Coming soon, as described in the PDF.
2. **Talk to Fahem:** one question at a time; typing always works. Voice shows recording, transcribing, transcript review, permission denied and retry states. Do not imply a live voice conversation if only transcription exists.
3. **Review your profile:** idea, offers, needs, commitment, runway, location and dealbreakers. Every extracted fact has “You said…” evidence. Save edits, then explicitly confirm before searching.
4. **Meet your matches:** 3–5 people, a complementary-fit summary, two or three evidence-backed reasons, and Request intro / Pass. Label seeded people “Demo profile.” A score is optional; prioritize understandable reasons.
5. **Candidate detail:** their offer, their need, reciprocal fit, relevant constraints, evidence and Request intro. Keep contact details absent until acceptance.
6. **Introductions:** Received, Sent, Accepted and Closed states. Recipient accepts or declines; requester sees Pending. Accepted unlocks contacts for both. Handle duplicate requests and stale status.

Desktop: navigation + conversation + workspace. On narrow screens, show one primary surface at a time with a clear way back to the conversation. This mobile behavior is proposed, not observed in Jack & Jill.

Keep Fahem and Wasel within one coherent app: label which agent is speaking and hand off visibly after profile confirmation. Users should not have to maintain two disconnected conversations.

## Agree on data handoffs first

Member 4 writes one shared contract; all four build against identical examples. Suggested concepts, not existing endpoint claims:

- `InterviewTurn`: session id, question id, user text, agent reply, completion state.
- `Profile`: id, version, structured facts, evidence references and confirmed state. Separate public matching facts from private contact data.
- `Match`: profile id, profile versions used, rank, optional formula score, evidence-backed reasons and introduction status. No private contact fields.
- `Introduction`: id, requester id, recipient id, status and timestamps. Only the recipient can accept an incoming request.

Essential operations: advance interview, extract draft profile, save/confirm profile, fetch matches, request intro, list received/sent requests, accept/decline request, fetch contacts after acceptance.

Frontend owner needs representative responses immediately: incomplete interview, valid draft, extraction error, successful matches, no matches, pending intro and accepted intro. Build against those while the model work proceeds.

Profile edits must invalidate or recompute matches based on the old version. Two sessions must not accidentally share identity. Contact protection belongs on the server, not in hidden frontend markup.

## Integration order

1. **First 30 minutes:** agree names/owners, main demo scenario, profile fields, response shapes and the existing implementation to reuse. Rigad sketches the six screens; member 4 creates the shared examples.
2. **First working milestone:** Rigad connects screens with sample responses; Fahem produces one real profile; Wasel returns one ranked batch; backend saves two separate users and one introduction.
3. **First integration:** connect text interview → profile confirmation → real match result. Resolve data mismatches here, before visual polish.
4. **Complete the two-person loop:** request in session A, accept in session B, contacts become available to both. Test decline, repeated clicks and reload.
5. **Then polish:** voice transcription, transitions, responsive layout, friendly errors and a short reliable presentation route. Preserve the text path if speech fails.
6. **Freeze:** rehearse on the actual demo machine and deployed link. Record a fallback walkthrough and disclose cached/model-unavailable behavior honestly.

These are relative milestones, not a verified hackathon deadline.

## Stack and existing workspace

The supplied PDF proposes Gradio, Hugging Face, SQLite, speech transcription and embeddings. The workspace already contains multiple earlier prototypes: root Karak code and `founders-ai/`, whose files include a Gradio app, UI, profile schemas, matching and storage modules. Their current functionality has not been run or verified in this review.

Before creating a third app, member 4 and Rigad should choose a reusable base. If the deadline is close, first reproduce the core layout and behavior within that base. If exact interaction control is essential and there is enough integration time, consider a custom frontend over the shared Python services. That is a scope decision, not an instruction to migrate now.

Do not mix older Karak terminology, investor flows or other prototype assumptions into Fahem & Wasel without an explicit product decision. The supplied cofounder brief is the reference for this plan.

## Acceptance checks

- Two people independently complete the interview and confirm their profiles.
- Missing information is requested or visibly unknown, never invented.
- Hard constraints exclude incompatible profiles before ranking.
- Reasons accurately reference both people's statements; unknown facts do not become confident reasons.
- A legitimate no-match state gives a useful refinement action.
- Contacts cannot be retrieved before recipient acceptance, including by direct request.
- Declining does not reveal contacts; repeated request/accept clicks do not create duplicates.
- Refresh preserves the agreed session and intro state; the presenter can reset demo data predictably.
- Keyboard navigation, visible focus, readable contrast, touch targets and reduced motion work.
- Slow models, failed transcription and network failures have clear retry/recovery states.

## Review limits

This is a detailed inspection of the available signed-in candidate dashboard, not a complete reverse engineering of Jack & Jill. Signup, recruiter/Jill views, live calls, recording, message generation, uploads, successful mutations, every hover/focus state, all breakpoints and the full animation set remain untested. No proprietary source or assets were copied. Visual measurements are reference observations; the proposed product behavior is a recommendation.
