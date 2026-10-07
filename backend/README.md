# Patchlane Supabase backend

The separate Lahore pilot project **Patchlane Lahore Pilot** is active in Mumbai (`ap-south-1`). Three migrations are applied. The database remains empty: **0 provider rows** and **0 verification events**. Supabase estimated **$0/month** at creation; no paid upgrade was accepted.

## Public directory boundary

The app reads only `public.provider_directory`. Its seven fields are `id`, `display_name`, `public_area_label`, `public_phone`, `verified_at`, `verification_valid_until`, and `updated_at`. A row appears only if it is published, explicitly consented for public listing and phone display, currently verified, and matched to the latest verification event. A failed later check or expired window hides the listing.

The public view uses `security_invoker=true` and `security_barrier=true`. To avoid giving clients access to the private provider table, the view calls `private.public_provider_directory_rows()`, a `SECURITY DEFINER` accessor with an empty `search_path`. It returns only the approved seven columns and repeats the publication, expiry, consent, and current-event gates. Anonymous and authenticated roles may execute that safe accessor but have no SELECT on `private.providers` and cannot read the internal verification status or verification-event log. The `private` schema is not exposed through PostgREST. Provider onboarding and verification-event insertion remain trusted-server operations; no service-role key belongs in the app or repository.

## Checks performed

The anonymous REST request to `public.provider_directory` returned **HTTP 200** with `[]`, as expected for the empty database. Requesting the `private` schema through PostgREST returns `PGRST106`; only `public` and `graphql_public` are exposed. Database privilege checks confirm anonymous roles cannot read private provider records or the internal verification status.

These checks exercise the access boundary with an empty database; no real provider row was inserted to validate a populated directory. No provider name, phone, consent, or verification evidence has been collected or imported.

## App behavior and remaining operations

With public settings configured, the mobile app makes an area-filtered read-only GET. It does not request rider location or write to Supabase. Before it opens the phone dialer, it queries the provider ID again from the same consent- and verification-gated public view. A revoked, expired, removed, or unreachable listing blocks the handoff. If the recheck succeeds, the rider may tap **Open phone dialer**; Android/iOS presents the device phone app and the rider chooses whether to place a call. Patchlane does not directly place a call, send a message, book, dispatch, or receive a contact-status signal.

A functioning local service still needs an approved provider opt-in/source, documented consent, current verification and renewal procedures, an accountable operator, and rider-support arrangements. The directory is empty and provider onboarding is not implemented; this pilot is not production-ready. Recheck costs before any plan change or paid add-on; no paid upgrade has been accepted.

`python3 tests/backend_contract_audit.py` checks migration guardrails. `python3 tests/live_directory_smoke.py` checks the UI against an isolated local mock; it does not send fixture data to Supabase or validate real provider evidence.
