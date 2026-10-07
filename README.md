# Patchlane

Patchlane is an area-search pilot for motorcycle puncture help. The live directory is currently empty, so the app may find no providers. It is not yet an operating roadside service and should not be presented as production-ready.

## What the app does

With the public Supabase settings configured, a rider enters an area or landmark and the app reads only `public.provider_directory`. The backend returns the seven approved fields only when a listing is published, has current verification, matches the latest verification event, and carries explicit public-listing and phone-display consent. Before opening the phone dialer, the app re-reads that provider by ID from the same gated public view; an expired, removed, revoked, or unreachable listing fails closed. The rider decides whether to place a call. Patchlane does not take a booking, dispatch a mechanic, or guarantee availability.

Without both public settings, Patchlane opens a separate `Demo · fictional` flow. Its providers, sample areas, distances, ETAs, phones, and availability are fictional. Request and provider-listing screens are explicitly previews: nothing is sent, saved, or published. These screens are not provider signup or onboarding.

Patchlane does not request device location. The location SDK and runtime location code have been removed. The regenerated Android manifest has only `INTERNET` as an active permission; location, storage, overlay, and vibration permissions have merge-removal directives. App data backup is disabled while the pilot has no account or local data model.

## Development and checks

```bash
npm ci
npm run check
npm run build:web
python3 tests/accessibility_audit.py
npm test
```

`npm test` runs the backend contract audit, native configuration checks, browser tests for the fictional flow, and isolated browser tests for the live pilot. The live test uses only a local request interceptor and a test-only publishable placeholder; its single provider fixture never reaches Supabase. Tests cover successful, empty, and failed reads; a listing revoked after search; expired verification; network failure during the contact recheck; sample-only request/listing previews; responsive layouts; and 48 px touch targets. The checks also regenerate mobile web QA captures in [`screenshots/`](./screenshots/). These web captures are not native Android store screenshots.

The latest EAS `preview` build is an internal APK, **not a Google Play release**. It was built from source commit [`f8ab047`](https://github.com/pakmultilinks-dot/puncture-rescue-app-v5/commit/f8ab0472f9bc52a5346d57ae49e70c20c2b3fda0), app version `5.0.0`, Android build number `2`. [Open build details](https://expo.dev/accounts/kominman/projects/patchlane-puncture-demo-v5/builds/d1c3274f-f7ca-45ad-8502-cbeb50f0a2af) or [download the review APK](https://expo.dev/artifacts/eas/y1r-VeYOEV31b-9Swl12ay2GquDhlVCE-SOQQt5BiEQ.apk). Increase `versionCode` before the next Play upload. Expo SDK 57 resolves Android target API 36 in the current prebuild.

## Backend status

The separate Supabase project **Patchlane Lahore Pilot** is in Mumbai (`ap-south-1`). Its three migrations define the unified provider record, private verification-event log, and guarded public directory. The anonymous directory request returned HTTP 200 with `[]`; database checks found **0 provider records and 0 verification events**. No real provider data was invented, imported, or published.

The database and read-only app plumbing exist, but the live service still needs an approved provider source, opt-in consent, verification and renewal operations, an accountable operator, and rider-support arrangements. No provider admin workflow, moderation, messages, booking, payments, or dispatch exists in this build. See [`backend/README.md`](./backend/README.md) and [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md).

## Public-release blockers

Before a Play submission, Patchlane needs real, currently verified and explicitly consented providers, a public privacy policy based on confirmed service/log retention and an accountable publisher contact, an accurate Play Data safety declaration, and a completed store listing. The current screenshots are test captures, not store marketing assets, and no physical-device or emulator test has been completed. If the owner's Play account is a personal account created after 2023-11-13, Google requires a closed test with at least 12 opted-in testers for 14 consecutive days before applying for production access.

The current npm audit has **15 high advisories** and no moderate findings after a scoped UUID update for Xcode tooling. The remaining `braces` and `node-forge` advisories have no patched releases published. Do not run `npm audit fix --force`: npm proposes downgrading Expo to 44 and React Native to 0.72, which would break the supported SDK line. See [`RELEASE_READINESS.md`](./RELEASE_READINESS.md) for the launch gates and official Play requirements. A privacy-policy working draft is in [`PRIVACY_POLICY_DRAFT.md`](./PRIVACY_POLICY_DRAFT.md); it is not approved or publishable as-is.
