# Patchlane v5 — puncture-help review build

Patchlane is still a provisional placeholder name. v5 is a standalone mobile-first concept for one task: finding and contacting a motorcycle puncture mechanic. An individual mechanic and a shop share the same listing form and appear in the same rider flow. This is a local sample app, not a live roadside service.

## Run and test

From this folder:

```bash
npm ci
npm run check
npm run build:web
python3 tests/accessibility_audit.py
npm test
```

`npm test` runs an Expo web export, then six local Chromium/Playwright groups. They cover the rider start, tap-only location check, denied-permission area entry, synthetic sample list, profile and request/cancel preview, no-results recovery, one shared sample listing form, and responsive layout. Button targets and overflow are checked at 360, 390, 430 and 768 CSS pixels. The screenshot suite renders 390 × 844 CSS-pixel views.

The browser permission/location state is mocked for repeatability; this does **not** test a native permission prompt or device behavior. The v5 UI and tests do not send location, place calls, send requests or messages, create listings, or connect to a backend.

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

See [`DESIGN_REVIEW.md`](./DESIGN_REVIEW.md) for the visual changes, [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) for state and privacy boundaries, and [`TEST_REPORT.md`](./TEST_REPORT.md) for the local QA results and limitations.

## Scope and data

Every mechanic name, area, phone number, distance, availability window and ETA is fictional. Phone numbers use only `000 000 0000`. One short `Demo · fictional` indicator stays in the header; contextual notes clarify the location and estimate behavior at the relevant decision points. Location is requested only after the primary rider action is tapped, then the single foreground fix is discarded; sample results are not matched to coordinates.

There is no real map, provider coverage, account, registration, call, booking, message, notification, payment, dispatch, location transmission or backend. No additional roadside service categories were added. The carried dependency-audit snapshot records 23 advisories (16 high, 7 moderate, 0 critical), while a cache-only `npm audit --offline` returned zero; because those results conflict and no live registry audit was run, treat dependency status as unresolved. No dependency versions were upgraded.

## Release status

The v5 source is isolated from the v4 project. The existing public [v3 repository](https://github.com/pakmultilinks-dot/puncture-rescue-app-v3) and earlier EAS build remain unchanged. The approved v5 source is published in the new [public GitHub repository](https://github.com/pakmultilinks-dot/puncture-rescue-app-v5). Its dedicated [Expo project](https://expo.dev/accounts/kominman/projects/patchlane-puncture-demo-v5) uses Android package ID `com.kominman.patchlane`.

The internal Android APK preview is ready. Open the [Expo build/install page](https://expo.dev/accounts/kominman/projects/patchlane-puncture-demo-v5/builds/0dd64627-e58f-427b-8938-7519f598def5) on an Android device, or [download the APK directly](https://expo.dev/artifacts/eas/zLfvMwstj_dpyqZlAIpVvU3qgKJpHLOhtwvtcnvKCGM.apk). The APK download was verified with HTTP 200 on 2026-10-06. EAS lists the build expiration as **2026-10-20 09:59 UTC**.

EAS built the app from source commit `82b1e8342502e56fcbcff5ea006812475821c2f4`. The final GitHub branch includes a later documentation-only release/QA update; app code, package ID and dependencies were not changed after the build upload. This is an internal preview only, not an app-store release. A remote APK build does not imply native-device validation: no emulator, simulator, or physical-device behavior was tested.

## Live-service foundation — not deployed

On 2026-10-07, a Supabase-compatible PostgreSQL migration was added as a secure starting point for a single unified mechanic/shop provider directory. It requires current provider verification plus separate recorded consent to publish the listing and public contact number; row-level security hides incomplete, paused, unverified, expired, or unconsented records. The migration contains no provider seeds and excludes rider coordinates and exact addresses. The new static SQL guardrail audit is included in `npm test`.

This does **not** connect a backend or add real providers. The app remains a fictional-data demo, and calls, bookings, messages, payments, and dispatch remain disabled. See [`backend/README.md`](./backend/README.md) for what is prepared and the remaining account, market/region, provider-permission, verification, and operational decisions. The migration has not been run against a provisioned database; its static test is not a live RLS test.
