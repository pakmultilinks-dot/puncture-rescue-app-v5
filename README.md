# Patchlane

Patchlane is a focused motorcycle-puncture-help pilot. The rider app can search the Lahore pilot’s read-only directory by area or landmark. It displays only listings returned by the public Supabase view, whose database gate requires current verification plus explicit listing and phone-display consent. The directory currently has **no provider listings**, so live mode correctly returns an empty state; Patchlane is **not ready to operate as a roadside service**.

## Run and test

```bash
npm ci
npm run check
npm run build:web
python3 tests/accessibility_audit.py
npm test
```

For a local live-mode build, copy `.env.example` to `.env` and replace its publishable-key placeholder with the project’s **publishable** Supabase key. Without both `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, the app shows a clearly marked fictional demo. The internal Android preview receives those two public client settings from the EAS `preview` environment. Never put a service-role key in the app, `.env`, EAS preview variables, or the repository.

`npm test` runs the backend static audit, the existing six local mobile/browser groups, and `tests/live_directory_smoke.py`. The live-mode browser test builds with a reserved test hostname and a test-only publishable placeholder, then intercepts requests locally. Its one fictional provider is held only in the test process: it is never sent to Supabase or committed as live data. Test coverage includes the exact seven-field GET query, success/empty/error states, and checks that live mode does not request rider location or enable calls, messages, or requests.

The browser location checks are mocked. They do not test a native permission prompt, an Android/iOS runtime, or physical-device behavior. Screenshots under [`screenshots/`](./screenshots/) are explicitly fictional-demo captures, not live provider data. See [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md), [`TEST_REPORT.md`](./TEST_REPORT.md), and [`backend/README.md`](./backend/README.md) for the current implementation and backend boundary.

## Data and rider behavior

When live configuration is present, Patchlane asks for an area or landmark and sends a read-only `GET` to `public.provider_directory`. It requests only `id`, `display_name`, `public_area_label`, `public_phone`, `verified_at`, `verification_valid_until`, and `updated_at`. The client does not query the private provider table, write provider records, save location, or send a lead. It does not request rider location in live mode. A consented public phone number is plain text; tap-to-call, messaging, booking, payments, and dispatch are not enabled.

If client configuration is missing, the separate local-review flow uses fictional names, sample areas, zero-only phone numbers, and fictional estimates. It is identified by `Demo · fictional`; its request and listing screens are previews only. Those fixtures are not seeded, imported, or used by the live directory.

## Backend status

The separate Supabase project **Patchlane Lahore Pilot** is healthy in Mumbai (`ap-south-1`). Supabase’s creation estimate was **$0/month**; no paid upgrade was accepted. Three migrations define the unified provider record, append-only verification events, the verified-and-consented public view, and a narrow server-owned accessor that lets the invoker-rights view work without giving anonymous clients access to the private base table.

The anonymous REST endpoint was checked end to end and returned **HTTP 200 with `[]`**. A request for the `private` schema was rejected because only `public` and `graphql_public` are exposed. Database checks confirm **0 provider rows**, **0 verification events**, no anonymous SELECT on `private.providers`, and no anonymous read of the internal verification-status field. No real provider details have been collected, imported, or published.

The backend and app plumbing are in place, but a real directory still depends on an approved provider opt-in/source, explicit consent, a documented verification and renewal process, and an accountable operator to maintain records. Provider onboarding, moderation, calls, messages, bookings, payments, dispatch, and service support are not provided by this build. Do not describe it as production-ready while those conditions and actual provider data are absent.

The source is in the existing [Patchlane v5 GitHub repository](https://github.com/pakmultilinks-dot/puncture-rescue-app-v5). The separate Expo Android preview is an internal review build, not an app-store release. The project region is a data-location choice, not proof of legal or regulatory compliance. Dependency status remains unresolved: the carried audit snapshot lists 23 advisories while a cache-only offline audit reported none; no live registry audit or dependency upgrades have been performed.
