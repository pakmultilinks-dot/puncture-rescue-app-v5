# System design

The app has six client-side screens: `home`, `area`, `results`, `profile`, `request`, and `listing`. Form values, selected mechanic, location state and request status remain in component memory only.

The rider starts with one primary puncture-help action. Only its tap requests foreground location permission. If granted, one foreground location fix is checked and discarded; the app then shows clearly labeled synthetic examples that are not matched to coordinates. If permission is denied or the check fails, the rider lands on the dedicated area/landmark entry screen. Manual entry never requests location. “Central sample area” and “East sample area” return hard-coded fictional examples; other text leads to an empty result with an editable recovery path.

Sample mechanic rows open a concise fictional profile. Distance, ETA, availability, phone and area are examples; the phone is always `000 000 0000`. The profile CTA opens a simulated request status. Cancel changes only local state. No call is placed and no request, location, booking, notification or message is sent.

The mechanic/shop preview uses one form for display name, zero-only sample phone and coverage area. It has no provider-type selector, service categories, account, backend or persistence. A valid form reveals a local preview; nothing is saved or published.

A small persistent `Demo · fictional` header marker applies across screens. Short supporting notes disclose location matching, sample estimates, and the non-contactable phone at the point they matter. There is no real map, provider coverage, live provider search, location transmission, payment or emergency dispatch.

## Backend foundation deployed 2026-10-07 — app remains demo-only

A separate, healthy Supabase project for the Lahore pilot is in Mumbai (`ap-south-1`). The provider-directory migration is applied and defines one unified provider record, an internal verification-event log, and a caller-rights public directory view. Public reads are constrained to published listings with current verification and explicit listing/contact consent; public roles cannot write providers or read verification events.

Live metadata checks confirmed row-level security, `security_invoker=true`, the expected public columns and blocked write permissions. The database currently contains zero provider rows and zero verification events. The mobile app does not call Supabase and continues to show only fictional samples; no real provider data or contact paths were added.

A live directory is still blocked on permitted provider sourcing/opt-in, provider consent, a documented verification and renewal process, and an accountable operator. The app must remain demo-only until those gates and end-to-end REST/RLS checks are completed. Calls, bookings, messages, payments and dispatch are not enabled.
