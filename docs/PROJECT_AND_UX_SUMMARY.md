# Project and UX Summary

## Project Overview

**Thesidia** (web brand: **Katanx**) is a hybrid AI and social platform:

- **AI**: Synthesis-based intelligence (Thesidia), Gnostic Blade protocol, Sophia memory (7-layer gnostic map), deep research, two-mode responses (Regular/Narrative).
- **Social**: Twitter-like feed (stream), profiles, KIM messaging, posts, bot detection, multi-user auth.
- **Stack**: Flask backend, vanilla JS frontend, SQLite/JSON storage, Ollama/MLX for local inference.

Landing positioning: "Social media for people who actually do stuff" and "No influencers, only practitioners" across nine arts (Martial, Movement, Visual, Internal, Performance, Healing, Intellectual, Invention, Leadership).

---

## Current UX Architecture

### Entry Points

| Route | Served As | Purpose |
|-------|-----------|---------|
| `/` | `landing.html` | Marketing: hero, manifesto, Nine Arts, platform cards, Thesidia AI, CTA to Join / Try AI |
| `/auth.html` | Auth page | Sign In / Sign Up (phone, email, OAuth mock in dev) |
| `/stream.html` | Stream | Main feed; sidebar; KIM; onboarding integration |
| `/profile` | `profile.html` | User profile; onboarding + profile customization |
| `/contexts` | `contexts.html` | Thesidia chat (contexts) |
| `/application` | `application.html` | Application layer / dashboard |
| `/explore`, `/search` | `search.html` | Search/explore |
| `/landing-v3.html` | Alternate landing | V3 landing (feature flags, animations) |

### Auth and Post-Auth Flow

- **Session**: `thesidia_user_id`, `thesidia_session_id` (and `thesidia_token` when used) in `localStorage`.
- **Post-login/register (phone, email, OAuth)**: `auth.js` always redirects to `window.location.href = '/'`.
- **Root `/`**: Serves `landing.html` regardless of auth. No redirect for logged-in users.
- **Result**: New and returning users both see landing after sign-in. There is no automatic send to stream, app, or onboarding.

### Onboarding System (Existing)

- **Scope**: `webapp/js/onboarding/` (utils, manager, tutorials, profile-customization, integration) and `webapp/css/onboarding.css`.
- **Integration**: `integration.js` + `onboarding.css` are included only on **`profile.html`** and **`stream.html`**.
- **State**: `localStorage`: `onboarding_enabled`, `onboarding_progress` (e.g. `firstVisitCompleted`), `tutorials_completed`, `profile_customization`.
- **Trigger logic**:
  - If `!progress.firstVisitCompleted` → show **Welcome** (full-screen overlay).
  - Else, page-specific: Profile → profile-setup; stream → stream-navigation; explore → explore; kim → kim-chat. Posting and profile-customization are available but not auto-wired in the same way.
- **`getCurrentPage()`**: `profile`, `stream`, `explore`, `kim`, `landing` (for `/` or path containing `landing`), else `unknown`. `app.html`, `contexts.html`, `application.html` resolve to `unknown`.
- **Welcome** only runs when a page that loads `integration.js` is hit (profile or stream). First load on `contexts` or `application` does not run onboarding.
- **Feature flag**: `OnboardingUtils.isEnabled()`: `?onboarding=false` or `onboarding_enabled=false` in localStorage disables. Default: enabled on localhost/127.0.0.1.

### Page Detection and Gaps

- **Stream, profile, explore, kim**: Detected; onboarding can run there when integrated.
- **Landing**: Detected as `landing` but `integration.js` is not loaded on `landing.html`, so no onboarding.
- **Contexts, application, app, index**: `unknown`; no onboarding integration.
- **Auth**: No onboarding; auth is pre-sign-up/sign-in.

---

## UX Observations

1. **Post-auth destination**: Sending everyone to `/` (landing) after login underuses the product. Logged-in users likely expect feed or app, not marketing.
2. **Onboarding surface**: Limited to profile and stream. Users entering via contexts, application, or app bypass onboarding.
3. **"First visit"**: Tied to localStorage and to loading a page with `integration.js`. Clearing storage or first landing on a non-integrated page effectively resets or skips onboarding.
4. **No explicit onboarding route**: There is no `/onboarding` or `/welcome` in the main flow. Onboarding is contextual overlays on existing pages, not a dedicated step.
5. **Landing vs app for authenticated users**: No distinction; both see the same landing.
6. **Profile customization**: Implemented for own vs others’ profile and customization panel; depends on being on `profile.html` with integration.

---

## Design and Theming

- **Landing**: Inconsolata (headings), Inter (body); dark `--space-black`; yellow `#ffd700`, tan, blue accents; typewriter hero, Nine Arts grid, cards, toast/skeleton, reduced motion, basic a11y (skip link, live regions, focus).
- **Auth**: Space Grotesk, `--theme-neon`, `--bg-primary/secondary`, tabs, form and phone flows.
- **Onboarding**: `onboarding.css`; full-screen welcome, bottom-sheet for other tutorials; 44px touch targets, swipe-to-dismiss; uses `--bg-secondary`, `--border-color` where available.

---

## Relevant Files (Quick Reference)

| Area | Paths |
|------|-------|
| Landing | `webapp/landing.html`, `landing-v3.html`, `landing/` |
| Auth | `webapp/auth.html`, `auth.js`; `server.py` `/api/auth/*` |
| App shell / nav | `webapp/app.js`, `application.html`, `contexts.html`, `stream.html` |
| Onboarding | `webapp/js/onboarding/*`, `webapp/css/onboarding.css`, `webapp/onboarding.html` (test) |
| Server routing | `webapp/server.py` (`/`, `/home`, `/auth.html`, `/stream`, `/profile`, `/contexts`, `/application`, `/api/onboarding/*`) |

---

*Last updated: 2026-01-24*
