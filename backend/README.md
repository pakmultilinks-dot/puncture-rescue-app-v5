# Patchlane Supabase backend

The separate Lahore pilot project **Patchlane Lahore Pilot** is active and healthy in Mumbai (`ap-south-1`). Supabase estimated **$0/month** at creation; no paid upgrade was accepted. Three migrations are applied. The database remains empty: there are **0 provider rows** and **0 verification events**.

## Public directory boundary

The app reads only `public.provider_directory`. Its seven fields are `id`, `display_name`, `public_area_label`, `public_phone`, `verified_at`, `verification_valid_until`, and `updated_at`. A listing is returned only when it is published, explicitly consented for public listing and phone display, currently verified, and matched to the current latest verification event. A later failed check hides the listing. Future-dated and expired verification windows do not qualify.

The public view uses both `security_invoker=true` and `security_barrier=true`. To avoid granting clients access to the private provider table, the view calls `private.public_provider_directory_rows()`, a `SECURITY DEFINER` accessor with an empty `search_path`. It returns only the seven approved columns and repeats the publication, expiry, consent, and current-event gates. Anonymous and authenticated roles may execute only that safe accessor; they have no SELECT privilege on `private.providers` and no read access to the internal verification status or verification-event log. The `private` schema is not exposed through PostgREST. Provider onboarding and verification-event insertion remain trusted-server operations; no service-role key belongs in the mobile app or repository.

## Checks performed

The anonymous REST request to `public.provider_directory` now returns **HTTP 200** with `[]`, consistent with the empty database. Requesting the `private` schema through PostgREST returns `PGRST106` and confirms the API exposes only `public` and `graphql_public`. Database privilege checks confirm anonymous roles cannot select from `private.providers` or read `verification_status`; the directory view remains caller-rights and exposes only its seven intended columns.

The SQL checks and the real REST request test the installed access boundary with an empty database. No real provider rows were added to exercise populated listing filters. No provider names, phone numbers, locations, consent, or verification evidence have been collected or imported.

## App configuration and remaining gates

The Expo client makes area-filtered `GET` requests only. Its EAS `preview` environment contains `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY`; both are public client settings, not service-role credentials. The app does not write to Supabase, ask for rider location in live mode, or initiate calls/messages/bookings. If either public setting is absent, the local app shows the clearly marked fictional demo; demo fixtures are test-only and are never inserted into production.

A live service still needs a permitted provider opt-in/source, explicit provider consent to display the listing and phone, a documented verification/renewal standard, and an accountable operator. The directory is empty and there is no support or response process, so this is not production-ready. Recheck cost before any plan change or paid add-on; none was accepted for this pilot.

`python3 tests/backend_contract_audit.py` checks the migration guardrails. `python3 tests/live_directory_smoke.py` verifies the live-mode UI against an isolated local mock. That test fixture is not sent to Supabase and does not validate populated production policies or provider evidence.
