# Patchlane v5 — puncture-help review build

Patchlane is still a provisional placeholder name. v5 is a standalone mobile-first concept for one task: finding and contacting a motorcycle puncture mechanic. An individual mechanic and a shop share the same listing form and appear in the same rider flow. The rider experience remains a synthetic-data demo, not a live roadside service.

## Run and test

From this folder:

```bash
npm ci
npm run check
npm run build:web
python3 tests/accessibility_audit.py
npm test
```

`npm test` runs an Expo web export, then the backend-contract audit and six local Chromium/Playwright groups. They cover the rider start, tap-only location check, denied-permission area entry, synthetic sample list, profile and request/cancel preview, no-results recovery, one shared sample listing form, and responsive layout. Button targets and overflow are checked at 360, 390, 430 and 768 CSS pixels. The screenshot suite renders 390 × 844 CSS-pixel views.

The browser permission/location state is mocked for repeatability; this does **not** test a native permission prompt or device behavior. The v5 UI and tests do not send location, place calls, send requests or messages, create listings, or connect to the provider directory.

## Screenshots

Fresh captures are under [`screenshots/`](./screenshots/):

- [Approval contact sheet](./screenshots/approval-contact-sheet.png) — rider start, sample mechanics, mechanic detail, and no-results recovery at native screenshot size.
- [Rider start](./screenshots/01-rider-start-390x844.png)
- [Denied location and area fallback](./screenshots/02-location-denied-fallback-390x844.png)
- [Nearby fictional mechanics](./screenshots/03-nearby-mechanics-390x844.png)
- [Mechanic profile](./screenshots/04-mechanic-profile-390x844.png)
- [Request preview and cancel](./screenshots/05-request-cancel-preview-390x844.png)
- [No-results recovery](./screenshots/06-no-results-390x844.png)
- [Shared mechanic/shop listing](./screenshots/07-unified-mechanic-listing-390x844.png)
- [Cancelled request preview](./screenshots/08-request-cancelled-390x844.png)

See [`DESIGN_REVIEW.md`](./DESIGN_REVIEW.md) for the visual changes, [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) for state and privacy boundaries, and [`TEST_REPORT.md`](./TEST_REPORT.md) for local QA and backend checks.

## Scope and data

Every mechanic name, area, phone number, distance, availability window and ETA shown in the app is fictional. Phone numbers use only `000 000 0000`. One short `Demo · fictional` indicator stays in the header; contextual notes clarify location and estimate behavior at the relevant decision points. Location is requested only after the primary rider action is tapped, then the single foreground fix is discarded; sample results are not matched to coordinates.

There is no real map, provider coverage, provider account, enrollment, call, booking, message, notification, payment, dispatch, location transmission, or live search in the rider app. A Supabase project now holds an empty, consent-gated provider-directory schema; it is not connected to Expo. The dependency-audit snapshot still records 23 advisories (16 high, 7 moderate, 0 critical), while a cache-only `npm audit --offline` returned zero; because those results conflict and no live registry audit was run, treat dependency status as unresolved. No dependency versions were upgraded.

## Backend status — project provisioned, app remains demo-only

A separate Supabase project named **Patchlane Lahore Pilot** is active in **Mumbai (`ap-south-1`)**, the nearest listed South Asia region used for this Lahore pilot ([Supabase region details](https://supabase.com/docs/guides/platform/regions)). Supabase reported an estimated project cost of **$0/month** at creation; no paid upgrade was accepted. Both PostgreSQL migrations are applied. They define one unified provider type, a restricted public directory view, verification-expiry checks, separate listing/contact consent requirements, and server-only provider writes. Publication must match an append-only, current verification event; a later failed check hides the listing. There are no seed rows, rider coordinates, or exact addresses.

Live database checks confirmed **0 provider rows and 0 verification events**, row-level security on both tables, `security_invoker=true` on the directory view, anonymous SELECT access to the view, no anonymous provider inserts, no authenticated provider updates, no anonymous access to verification events or internal verification status, and no service-role update/delete access to verification events. The view exposes only `id`, `display_name`, `public_area_label`, `public_phone`, `verified_at`, `verification_valid_until`, and `updated_at`. These checks verify installed permissions and an empty database; they do not test populated listing behavior or end-to-end REST access.

The Expo app remains disconnected from Supabase and continues to show only fictional examples. No real provider data has been collected or published; no provider consent or verification process has been carried out. Calls, bookings, messages, payments, and dispatch remain disabled. See [`backend/README.md`](./backend/README.md) for the remaining provider-onboarding, operations, and app-integration gates.

## Release status

The v5 source is isolated from the v4 project. The existing public [v3 repository](https://github.com/pakmultilinks-dot/puncture-rescue-app-v3) and earlier EAS build remain unchanged. The approved v5 source is published in the new [public GitHub repository](https://github.com/pakmultilinks-dot/puncture-rescue-app-v5). Its dedicated [Expo project](https://expo.dev/accounts/kominman/projects/patchlane-puncture-demo-v5) uses Android package ID `com.kominman.patchlane`.

The internal Android APK preview remains available. Open the [Expo build/install page](https://expo.dev/accounts/kominman/projects/patchlane-puncture-demo-v5/builds/0dd64627-e58f-427b-8938-7519f598def5) on an Android device, or [download the APK directly](https://expo.dev/artifacts/eas/zLfvMwstj_dpyqZlAIpVvU3qgKJpHLOhtwvtcnvKCGM.apk). EAS lists the build expiration as **2026-10-20 09:59 UTC**.

EAS built that APK from source commit `82b1e8342502e56fcbcff5ea006812475821c2f4`. The latest repository changes add backend schema, docs, and a test script; they do not change the mobile runtime, package ID, or dependencies, so no new Android build was made. The APK is still an internal demo preview, not an app-store release. A remote APK build does not imply native-device validation: no emulator, simulator, or physical-device behavior was tested.
