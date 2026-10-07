# Patchlane v5 test report

**Run date:** 2026-10-07. **Target:** Expo web exports and the approved Supabase project’s public API.

## Results

- `npm run check` — passed (`tsc --noEmit`).
- `npm test` — passed the backend static audit, all six existing browser groups, and the isolated live-directory browser test.
- `python3 tests/accessibility_audit.py` — all audited color pairs passed WCAG AA, with minimum contrast **4.78:1**.
- `python3 -m py_compile tests/*.py` and `git diff --check` — passed.
- The six existing browser groups cover the puncture-only rider start, tap-only location behavior in fictional demo mode, denied-permission fallback, fictional sample results, no-results recovery, local profile/request cancellation, the shared mechanic/shop preview, responsive layouts, and 48-pixel touch targets.
- `tests/live_directory_smoke.py` builds with a reserved mock hostname, clears Metro’s environment-sensitive cache, and intercepts the directory API locally. It checks the exact seven-field GET, current-listing UI, consented phone display without a contact action, no-results and network-error states, and that live mode never checks rider location. The test fixture is held only in the test process; it is not sent to Supabase.

The existing browser suite regenerates eight **390 × 844 CSS-pixel** fictional-demo screenshots. Browser geolocation is mocked; the suite does not test a native permission prompt or device location behavior.

## Supabase read-path verification

The active project `nuavjqyuquhmknwktxts` has all three migrations applied. A real anonymous GET to `public.provider_directory` returned **HTTP 200 with `[]`**. A request selecting schema `private` was rejected with `PGRST106`; PostgREST exposes only `public` and `graphql_public`. Database checks confirmed 0 provider rows, 0 verification events, no anonymous SELECT privilege on `private.providers`, no anonymous access to `verification_status`, and an invoker/barrier public view with the seven-field contract.

The REST test validates the read path while the directory is empty. It does not validate populated listing behavior, provider evidence, consent collection, native-app behavior, or ongoing verification operations. No provider records or verification events were inserted for testing.

## Release limits

The Expo `preview` environment uses only `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY`. No service-role key is in the client or repository. The local demo fixtures remain separate from the live backend, and live mode does not enable calls, messages, requests, bookings, payments, or dispatch.

This is not production-ready: there are no opted-in provider records and no documented sourcing, verification/renewal, support, or response process. No emulator, simulator, physical device, or native permission prompt was tested. The dependency-audit snapshot still reports 23 advisories while a cache-only offline audit returned none; with no live registry audit or upgrades, dependency status remains unresolved.
