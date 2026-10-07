# Patchlane v5 test report

**Run date:** 2026-10-07. **Source:** commit `f8ab0472f9bc52a5346d57ae49e70c20c2b3fda0`.

## Checks passed

- `npx expo install --check` — all Expo SDK 57 dependencies are compatible.
- `npm run check` — TypeScript passed with `tsc --noEmit`.
- `npm test` — passed the backend audit, native configuration audit, five fictional-demo browser groups, and the isolated live-directory browser test. The demo checks cover area entry, sample results, no-match recovery, fictional profile/request preview, the single sample listing preview, responsive widths, and 48 px touch targets.
- The live browser test passed success, empty, and network-failure states against an isolated local mock. Before phone handoff it checks a fresh ID-scoped public-view read; revoked listings, expired listings, and a failed recheck all block the dialer. The provider fixture is kept in the test process and is never sent to Supabase.
- `CI=1 npx expo prebuild --platform android --clean` — generated native Android files with no prebuild warnings. Only `android.permission.INTERNET` is active; location, storage, overlay, and vibration are removal directives. `allowBackup` resolves to `false`. Expo SDK 57's Gradle configuration falls back to target API 36.
- `python3 tests/accessibility_audit.py` — ten text/background pairs pass WCAG AA; the minimum ratio is **4.78:1** against a 4.50:1 threshold.
- `python3 -m py_compile tests/*.py` and `git diff --check` — passed.

The suite regenerates ten **390 × 844 CSS-pixel web QA screenshots** in [`screenshots/`](./screenshots/), plus a contact sheet. These are web renders, not Android emulator or physical-device captures.

## Internal APK

EAS build `d1c3274f-f7ca-45ad-8502-cbeb50f0a2af` finished successfully as an internal Android APK using profile `preview`. It reports app version `5.0.0`, Android build number `2`, and source commit `f8ab047`. [Open the EAS build](https://expo.dev/accounts/kominman/projects/patchlane-puncture-demo-v5/builds/d1c3274f-f7ca-45ad-8502-cbeb50f0a2af) or [download the APK](https://expo.dev/artifacts/eas/y1r-VeYOEV31b-9Swl12ay2GquDhlVCE-SOQQt5BiEQ.apk). The 68,416,874-byte download passed the ZIP integrity check; SHA-256: `47c1bf0a23fe41efe0aa1030298fbd1b0c448383e5ed1cfd8a99aef66ae7a9be`. This is an internal review build, not a Play Store submission.

## Backend and security status

The real anonymous GET to the Supabase public view returned HTTP 200 with `[]`. The project has **0 provider rows** and **0 verification events**. The test does not validate real provider consent, evidence, onboarding, or a populated production roster; it inserts no data.

After the SDK-compatible Expo update, removal of the unused location SDK, and a scoped/tested UUID 11.1.1 override for Xcode's single `uuid.v4()` call, the live npm audit reports **15 high and 0 moderate findings**. The reviewed [`braces` advisory](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) and [`node-forge` advisory](https://github.com/advisories/GHSA-86w9-cpqp-85rv) currently have no patched versions. `npm audit fix --force` was not used because it proposes downgrading Expo to 44 and React Native to 0.72.

## Limits

The APK has not been installed or exercised on a physical Android device or emulator. The native dialer handoff, keyboard/focus behavior, Android upgrade/install path, and real network behavior still require hands-on testing. The live directory also remains empty, so the browser fixture is not real service coverage. This is an internal pilot, not a public-service or store-readiness sign-off.
