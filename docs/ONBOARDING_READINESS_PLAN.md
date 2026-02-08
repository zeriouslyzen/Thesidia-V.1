# Onboarding Readiness Plan

## Objective

Make onboarding the default, predictable path for new users after sign-up/sign-in: welcome, core product intro, and (optionally) profile/stream setup, then hand off to the main app.

---

## Current State vs Target

| Aspect | Current | Target |
|--------|---------|--------|
| Post-auth redirect | Always `/` (landing) | Logged-in: app entry (`/stream` or `/home`); new users: onboarding entry |
| Onboarding entry | Only when visiting stream or profile with integration.js | Explicit post-auth path: welcome then stream (or chosen app home) |
| "First visit" | `localStorage` only; depends on hitting profile/stream | Persist `onboarding_completed` (and optionally `is_new_user`) server-side or in a stable client store; use for redirect and for "first visit" tutorials |
| Welcome surface | profile + stream only | All app entry points that load integration, or a dedicated `/welcome`/`/onboarding` step |
| Logged-in on `/` | Same as anonymous: full landing | Redirect to `/stream` or `/home` (or to onboarding if not yet completed) |

---

## Gaps (Prioritized)

### P0 – Routing and first-run path

1. **Post-auth always goes to `/`**  
   - `auth.js`: phone verify, email login/register, OAuth all use `window.location.href = '/'`.  
   - **Change**: Redirect to an "app home" (e.g. `/stream`) or to an onboarding entry (e.g. `/stream` with `?onboarding=welcome` or `/welcome`).

2. **No logged-in behavior on `/`**  
   - Root serves `landing.html` for everyone.  
   - **Change**: If `thesidia_user_id` (+ session) exists, redirect to `/stream` (or `/home`), or to onboarding if `!onboarding_completed`.

3. **No dedicated onboarding/welcome step**  
   - Welcome is an overlay on stream/profile. If the first loaded app page does not include `integration.js`, welcome never runs.  
   - **Change (recommended)**: Add `/welcome` (or `/onboarding`) as a 1–3 step flow (welcome, optional interests, "Go to Stream") that sets `firstVisitCompleted` and redirects to `/stream`. Alternative: ensure the default post-auth destination always loads integration and runs welcome there.

### P1 – Consistency of onboarding across app

4. **Integration only on `profile` and `stream`**  
   - `contexts`, `application`, `app`/`index` do not load `integration.js`. `getCurrentPage()` returns `unknown` for them.  
   - **Change**: Either (a) add `integration.js` (and `onboarding.css`) to `contexts.html`, `application.html`, and `app.html` and extend `getCurrentPage()` so welcome can run on first visit, or (b) rely on a dedicated `/welcome` and redirect so the first in-app page is always stream (or a single canonical app entry that has integration).

5. **`getCurrentPage()` and `unknown`**  
   - `utils.js`: `app`, `contexts`, `application` are not mapped.  
   - **Change**: If onboarding is shown on those pages, add cases (e.g. `contexts`, `application`, `app`) and define which tutorial (if any) runs there; or standardize on "only stream (and optionally profile) as first app page" and keep `unknown` as no automatic tutorial.

### P2 – Persistence and new-user detection

6. **Onboarding only in `localStorage`**  
   - Clearing storage resets progress; no server record.  
   - **Change**: Add `POST /api/onboarding/complete` (and optionally `GET /api/onboarding/status` with `onboarding_completed`, `is_new_user`) using `thesidia_user_id`. Auth middleware can attach `onboarding_completed` for client or server-side redirect. For MVP, optionally keep localStorage but fix the routing so "first app visit" is well-defined.

7. **New vs returning user**  
   - No `is_new_user` or `onboarding_completed` from backend.  
   - **Change**: On register (and optionally on first login from a new device), set `is_new_user` or `onboarding_completed=false`. Use in auth response and in `/` and post-auth redirect logic.

### P3 – Content and UX polish

8. **Welcome and tutorial copy**  
   - Align with Katanx/Thesidia positioning (practitioners, Nine Arts, AI, feed).  
   - **Change**: Review `tutorials.js` (welcome, profile-setup, stream-navigation, etc.) and any `/welcome` step; add 1–2 lines on Thesidia/KIM if those are in the main path.

9. **Profile and interests**  
   - Profile-setup tutorial exists; no explicit "pick interests" or "Nine Arts" step.  
   - **Change (optional)**: Add a step in `/welcome` or as a follow-up: choose 1–3 arts or tags to improve feed and profile defaults.

10. **Analytics and flags**  
    - `ONBOARDING_ROADMAP.md` and `ONBOARDING_SYSTEM.md` mention analytics and feature flags.  
    - **Change**: When wiring post-auth and `/welcome`, add minimal events: `onboarding_started`, `onboarding_completed`, `onboarding_skipped` (and `welcome_completed` if separate) for later analysis.

---

## Recommended Sequence

### Phase 1: Fix post-auth and root (P0)

1. **Auth redirect**  
   - In `auth.js`, after storing `thesidia_user_id` and session:  
     - If backend (or a new `/api/onboarding/status`) returns `onboarding_completed === false` or `is_new_user === true`: redirect to `/welcome` or `/stream?onboarding=welcome`.  
     - Else: redirect to `/stream` (or `/home`).  
   - If no backend yet: for MVP, always send to `/stream` (or `/stream?onboarding=welcome` and treat `?onboarding=welcome` as "force welcome if not completed").

2. **Root `/` when logged in**  
   - In `landing.html` or in a small inline script before main content: if `localStorage.thesidia_user_id` and `thesidia_session_id` exist, `location.replace('/stream')` (or `/home`).  
   - Optional: call `GET /api/onboarding/status` and, if `!onboarding_completed`, redirect to `/welcome` or `/stream?onboarding=welcome`.

3. **`/welcome` route and page (recommended)**  
   - In `server.py`: `@app.route('/welcome')` → `send_from_directory('.', 'welcome.html')`.  
   - `welcome.html`: 1–3 steps (e.g. Welcome to Katanx, What you can do, [optional] Pick 1–3 arts), "Go to Stream" / "Get started".  
   - On "Get started": set `firstVisitCompleted` (and call `POST /api/onboarding/complete` when it exists), then `location = '/stream'`.  
   - Reuse `onboarding.css` and, if useful, `OnboardingManager`/`TutorialRegistry` for consistency, or keep `/welcome` as a simple custom flow.

### Phase 2: Wire onboarding to app entries (P1)

4. **Ensure default app entry has onboarding**  
   - If post-auth and post-welcome always land on `/stream`: keep `integration.js` and `onboarding.css` on `stream.html`; ensure welcome runs when `?onboarding=welcome` or `!firstVisitCompleted`.  
   - If you add `/home` or another shell: either load integration there and run welcome, or redirect `/home` to `/stream` for first-time users.

5. **Optional: integration on `contexts` and `application`**  
   - Add the same two lines to `contexts.html` and `application.html`.  
   - In `utils.js`, `getCurrentPage()`: map `contexts` and `application`.  
   - In `onboarding-manager.js`, decide: run welcome on first visit to these pages, or only stream-navigation–style tips. For many products, running welcome only once (on stream or `/welcome`) is enough.

### Phase 3: Backend and persistence (P2)

6. **`GET /api/onboarding/status`**  
   - Extend existing handler to return `{ onboarding_completed: bool, is_new_user?: bool }` from DB or from a small user-metadata store keyed by `thesidia_user_id`.  
   - Auth middleware or a small `/`/landing script can use this for redirects.

7. **`POST /api/onboarding/complete`**  
   - Body: `{ }` or `{ step: 'welcome' }`.  
   - Sets `onboarding_completed=true` (and optionally `onboarding_completed_at`) for the current user.  
   - Called from `/welcome` "Get started" or from `OnboardingManager` when welcome is completed, if you prefer to keep welcome on stream.

8. **Register/first-login flags**  
   - In `/api/auth/register` and, if desired, in `/api/auth/login` when no prior session: set `is_new_user` or `onboarding_completed=false` so auth response and `/api/onboarding/status` stay in sync.

### Phase 4: Copy and analytics (P3)

9. **Tutorial and welcome copy**  
   - Update `tutorials.js` and `welcome.html` (or welcome overlay) to mention Stream, Thesidia, KIM, and practitioners/Nine Arts in 1–2 short lines.

10. **Events**  
    - In `OnboardingManager` and `/welcome`: send `onboarding_started`, `onboarding_completed`, `onboarding_skipped`, `welcome_completed` to your analytics or `event_collector.js` if present.

---

## Tasks Checklist

### Phase 1 (P0)

- [ ] **1.1** In `auth.js`, replace `'/'` with `/stream` (or with logic: `onboarding_completed ? '/stream' : '/welcome'` or `/stream?onboarding=welcome`).
- [ ] **1.2** On `landing.html` load: if `thesidia_user_id` and `thesidia_session_id`, redirect to `/stream` (or `/welcome` when `!onboarding_completed`).
- [ ] **1.3** Add `@app.route('/welcome')` and `welcome.html` with a short 1–3 step flow and "Get started" → set `firstVisitCompleted`, then `/stream`.
- [ ] **1.4** In `onboarding-manager.js` or `welcome.html`, support `?onboarding=welcome` to force welcome when the app home is stream.

### Phase 2 (P1)

- [ ] **2.1** Confirm `stream.html` (and, if used, `app.html`/`contexts` as app home) loads `integration.js` and `onboarding.css`.
- [ ] **2.2** (Optional) Add `integration.js` + `onboarding.css` to `contexts.html` and `application.html`; extend `getCurrentPage()` and `checkForTutorials` for `contexts`/`application` if you want contextual tips there.

### Phase 3 (P2)

- [ ] **3.1** Extend `GET /api/onboarding/status` to return `onboarding_completed` (and optionally `is_new_user`) from DB or user metadata.
- [ ] **3.2** Add `POST /api/onboarding/complete` and call it from `/welcome` or `OnboardingManager.completeTutorial('welcome')`.
- [ ] **3.3** In `/api/auth/register` (and optionally login): set `onboarding_completed=false` or `is_new_user=true` for new users.

### Phase 4 (P3)

- [ ] **4.1** Refresh welcome and `tutorials.js` copy (Katanx, practitioners, Stream, Thesidia, KIM).
- [ ] **4.2** Add `onboarding_started`, `onboarding_completed`, `onboarding_skipped` (and `welcome_completed` if separate) to analytics.

---

## Files to Touch (Summary)

| File | Changes |
|------|---------|
| `webapp/auth.js` | Post-auth redirect: `/` → `/stream` or `/welcome`/`/stream?onboarding=welcome` using onboarding status when available. |
| `webapp/landing.html` | Inline or early script: if logged in, redirect to `/stream` or `/welcome`. |
| `webapp/server.py` | `@app.route('/welcome')`; extend `GET /api/onboarding/status`; add `POST /api/onboarding/complete`; in `/api/auth/register` (and optionally login) set `onboarding_completed`/`is_new_user`. |
| `webapp/welcome.html` | New: 1–3 step welcome, "Get started" → set progress and `POST /api/onboarding/complete`, then `location = '/stream'`. |
| `webapp/js/onboarding/utils.js` | Optional: `getCurrentPage()` for `contexts`, `application`, `app`; helper to read `?onboarding=welcome`. |
| `webapp/js/onboarding/onboarding-manager.js` | Optional: when `?onboarding=welcome` and not completed, show welcome; call `POST /api/onboarding/complete` on completion when API exists. |
| `webapp/js/onboarding/tutorials.js` | Copy updates for Katanx, practitioners, Stream, Thesidia, KIM. |
| `webapp/contexts.html`, `webapp/application.html` | Optional: add `integration.js` and `onboarding.css`; only if onboarding should run on those surfaces. |

---

## Out of Scope (For Later)

- A/B tests on welcome length or order.
- Localization.
- Profile-completion or interests as a hard gate before stream.
- Deeper gamification (badges, progress bar) beyond completion flags.

---

*Last updated: 2026-01-24*
