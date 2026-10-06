# v5 test report

**Run date:** 2026-10-05. **Target:** isolated v5 Expo web export, exercised locally.

## Results

- `npm run check` — passed (`tsc --noEmit`).
- `npm run build:web` — passed; the final `npm test` also ran the Expo web export as its `pretest` step.
- `npm test` — all six Playwright groups passed: puncture-only rider start and tap-only location; denied-location manual-area fallback and fictional mechanics; no-results recovery; mechanic detail and local request/cancel preview; one unified mechanic/shop listing; responsive screens and touch targets.
- `python3 tests/accessibility_audit.py` — all 10 audited foreground/background pairs passed WCAG AA normal-text contrast; minimum **4.78:1**.
- `python3 -m py_compile tests/smoke_mobile.py tests/accessibility_audit.py` — passed.

Browser checks mock geolocation permission/results. They verify permission is not checked before the rider taps, denied permission opens manual-area entry, and a granted location fix does not control sample matching. They also check one filled primary action on action screens, one persistent fictional-data marker, no horizontal overflow at 360/390/430/768 CSS pixels, and visible buttons at least **48 × 48 CSS pixels**. The results screen intentionally uses selectable mechanic rows instead of an extra CTA.

The suite regenerated eight individual screenshots at **390 × 844 CSS pixels** and visually reviewed the key rider flow. `screenshots/approval-contact-sheet.png` is a native-size 2 × 2 arrangement of rider start, sample mechanics, mechanic detail, and no-results recovery.

## Limits and advisories

The browser suite mocks web permission/location APIs. **No native permission prompt, simulator, emulator, physical device, or Android/iOS build was tested.** No EAS build or remote Expo action was run. The v5 app config remains detached from the existing EAS project.

The carried `dependency-audit.json` snapshot records **23 advisories: 16 high, 7 moderate, 0 critical**. A separate `npm audit --offline --json` run returned zero advisories from the local/offline audit data. Because that cache-only result conflicts with the carried snapshot and no live registry audit was made during this local-only phase, treat the dependency status as **unresolved**, not cleared. No dependency upgrades were made.

All provider names, areas, distances, ETAs, availability windows, and phone values remain fictional; phone values are `000 000 0000`. No call, request, message, listing, payment, or location was sent or saved. No Git remote was configured; no push, publication, deployment, or public/external change was made.
