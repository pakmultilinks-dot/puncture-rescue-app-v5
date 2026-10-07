# System design

The Expo app has six screens: `home`, `area`, `results`, `profile`, `request`, and `listing`. When both public Supabase settings are configured, the rider enters an area or landmark and the app makes an area-filtered read-only request to `public.provider_directory`. No rider GPS permission or location SDK is used; no rider account, search-history database, lead, provider write, booking, or dispatch is implemented.

The public view returns only `id`, `display_name`, `public_area_label`, `public_phone`, `verified_at`, `verification_valid_until`, and `updated_at`. The database gates each row on publication, explicit listing and phone-display consent, a current verification window, and the latest verification event. Empty results and network failure have separate, recoverable screens. A profile can show the public number and open the device dialer only after the rider taps. Before handoff, the app makes a fresh ID-scoped read of the same gated public view and checks expiry locally; removal, revoked consent, verification expiry, or a failed check blocks the dialer. The app does not place a call, send a message, or treat dialer opening as a completed contact.

Without both public client settings, the app uses a separate `Demo · fictional` mode with sample areas, zero-only phone numbers, and fictional distances, ETAs, and availability. Sample requests are labelled not sent; the mechanic/shop form is a local preview, not onboarding. No demo fixture is written to the backend. The browser tests use an in-process API mock and likewise do not insert rows.

## Backend access

The separate **Patchlane Lahore Pilot** Supabase project is in Mumbai (`ap-south-1`). Three migrations define one provider record per mechanic or shop, a private append-only verification-event log, and the public directory. `public.provider_directory` has `security_invoker=true` and `security_barrier=true`; it reads through `private.public_provider_directory_rows()`, a hardened `SECURITY DEFINER` accessor with an empty `search_path` that repeats the publication, expiry, consent, and latest-event checks. Anonymous clients have no SELECT privilege on private provider records and cannot read internal verification status or events. The `private` schema is not exposed through PostgREST. The mobile client uses only public URL and publishable-key settings, never a service-role key.

The anonymous REST request returned HTTP 200 with `[]`. The project currently has **0 provider rows** and **0 verification events**. No real provider details have been sourced or published. Provider onboarding, verification/renewal operations, support, and a functioning local coverage roster are still operational prerequisites.

## Android configuration

The managed app uses Expo SDK 57. The current prebuild resolves the Android target SDK fallback to API 36. `android.blockedPermissions` removes location, storage, overlay, and vibration permissions during manifest merge; `INTERNET` is the only active permission. App-data backup is disabled while the app has no account or data model. A branded 1024 px launcher icon and transparent adaptive-icon foreground are generated from the source SVGs in `assets/`.
