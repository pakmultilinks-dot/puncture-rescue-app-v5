# v5 test report

**Run date:** 2026-10-05 (local, pre-release QA). **Target:** isolated v5 Expo web export, exercised locally.

## Results

- `npm run check` — passed (`tsc --noEmit`).
- `npm run build:web` — passed; the final `npm test` also ran the Expo web export as its `pretest` step.
- `npm test` — all six Playwright groups passed: puncture-only rider start and tap-only location; denied-location manual-area fallback and fictional mechanics; no-results recovery; mechanic detail and local request/cancel preview; one unified mechanic/shop listing; responsive screens and touch targets.
- `python3 tests/accessibility_audit.py` — all 10 audited foreground/background pairs passed WCAG AA normal-text contrast; minimum **4.78:1**.
- `python3 -m py_compile tests/smoke_mobile.py tests/accessibility_audit.py` — passed.

Browser checks mock geolocation permission/results. They verify permission is not checked before the rider taps, denied permission opens manual-area entry, and a granted location fix does not control sample matching. They also check one filled primary action on action screens, one persistent fictional-data marker, no horizontal overflow at 360/390/430/768 CSS pixels, and visible buttons at least **48 × 48 CSS pixels**. The results screen intentionally uses selectable mechanic rows instead of an extra CTA.

The suite regenerated eight individual screenshots at **390 × 844 CSS pixels** and visually reviewed the key rider flow. `screenshots/approval-contact-sheet.png` is a native-size 2 × 2 arrangement of rider start, sample mechanics, mechanic detail, and no-results recovery.

## Limits and advisories

This was local, web-only QA. No native permission prompt, simulator, emulator, physical device, or Android/iOS build was tested. The later internal Android preview build is a separate release artifact and does not count as device validation.

The carried `dependency-audit.json` snapshot records **23 advisories: 16 high, 7 moderate, 0 critical**. A separate cache-only `npm audit --offline --json` run returned zero advisories. Because that result conflicts with the carried snapshot and no live registry audit was made, treat dependency status as **unresolved**, not cleared. No dependency upgrades were made.

All provider names, areas, distances, ETAs, availability windows, and phone values shown in the app remain fictional; phone values are `000 000 0000`. No call, request, message, listing, payment, or rider location was sent or saved by the app.

## Backend foundation — 2026-10-07

The static regression audit at `tests/backend_contract_audit.py` is part of `npm test`. It checks both migrations for consent and verification-event gates, limited read access, append-only audit records, no seed rows, and location/type minimization. The local type-check, web build, all six mobile smoke groups, static audit, accessibility audit and Python syntax checks passed on 2026-10-07. No mobile runtime screens or behavior changed.

A separate Supabase project for the Lahore pilot was created in Mumbai (`ap-south-1`) after approval; Supabase returned a project cost estimate of **$0/month**. Both SQL migrations are applied. Live checks found zero provider rows and zero verification events, RLS enabled on both tables, a `security_invoker=true` public directory view with seven intended columns, anonymous SELECT access to the public view, no anonymous provider inserts, no authenticated provider updates, no anonymous verification-event reads, and no anonymous access to the internal verification-status column. They also confirmed that the service role can insert verification events but cannot update or delete them, and that the provider read policy calls the current-event verification gate.

These live checks verify schema and grants but do not validate listing-filter behavior against records, end-to-end REST access, provider consent/evidence, or device behavior. No real provider information was imported, and the Expo app is not connected to the Supabase project. The app remains demo-only; calls, bookings, messages, payments and dispatch remain disabled.
