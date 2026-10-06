# System design

The app has six client-side screens: `home`, `area`, `results`, `profile`, `request`, and `listing`. Form values, selected mechanic, location state and request status remain in component memory only.

The rider starts with one primary puncture-help action. Only its tap requests foreground location permission. If granted, one foreground location fix is checked and discarded; the app then shows clearly labeled synthetic examples that are not matched to coordinates. If permission is denied or the check fails, the rider lands on the dedicated area/landmark entry screen. Manual entry never requests location. “Central sample area” and “East sample area” return hard-coded fictional examples; other text leads to an empty result with an editable recovery path.

Sample mechanic rows open a concise fictional profile. Distance, ETA, availability, phone and area are examples; the phone is always `000 000 0000`. The one profile CTA opens a simulated request status. Cancel changes only local state. No call is placed and no request, location, booking, notification or message is sent.

The mechanic/shop preview uses one form for display name, zero-only sample phone and coverage area. It has no provider-type selector, service categories, account, backend or persistence. A valid form reveals a local preview; nothing is saved or published.

A small persistent `Demo · fictional` header marker applies across screens. Short supporting notes disclose location matching, sample estimates, and the non-contactable phone at the point they matter. There is no real map, provider coverage, live service, location transmission, payment or emergency dispatch.
