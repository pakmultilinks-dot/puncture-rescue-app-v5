# System design

The app has six screens: `home`, `area`, `results`, `profile`, `request`, and `listing`. With public Supabase client settings configured, the rider enters an area or landmark and the app makes one read-only search of `public.provider_directory`. The app does not ask for location in live mode, persist rider information, write provider rows, send a lead, or contact a mechanic.

The live results and profile are populated only from the database’s seven-field public view. The view is gated by publication status, current verification, explicit listing and phone-display consent, and a matching latest verification event. Public phone numbers are shown as text only; Patchlane does not create a tap-to-call action. Live profiles do not offer a request preview, and calls, messages, bookings, payments, and dispatch remain disabled. Network failures and empty results have separate recovery states.

Without both public client settings, the local app displays `Demo · fictional` and uses only isolated examples: sample areas, zero-only phone numbers, and fictional distances, ETAs, and availability. The location permission flow and request/cancel screen exist only in that fictional demo path. Its shared mechanic/shop form is a local preview; nothing is submitted or saved. Test fixtures for live-mode UI checks are returned by an in-process browser mock and are never written to the database.

## Backend access

The separate **Patchlane Lahore Pilot** Supabase project is in Mumbai (`ap-south-1`). Three migrations define one provider record per mechanic or shop, a private append-only verification-event log, and the public directory. `public.provider_directory` has `security_invoker=true` and `security_barrier=true` and exposes only the approved seven public columns. It reads through `private.public_provider_directory_rows()`, a hardened `SECURITY DEFINER` function with an empty `search_path` that rechecks publication, expiry, both consent records, and the latest verified event. Anonymous clients have no SELECT privilege on the base table or access to internal status/event fields. The `private` schema is not exposed via PostgREST.

An anonymous REST request to the public view returned HTTP 200 and an empty array. The project contains **0 provider rows and 0 verification events**. No real provider details have been sourced or published. The read path is connected, but provider onboarding, renewal/verification operations, and support remain prerequisites to a real service.
