# Patchlane Supabase backend — schema deployed, app not connected

A separate Supabase project for the Lahore pilot is active and healthy in **Mumbai (`ap-south-1`)**. Supabase returned a project-creation estimate of **$0/month**; no paid upgrade was accepted. The project is not the existing FleetFlow project. Both provider-directory migrations are applied, but no provider rows or verification events exist, and the Expo app does not yet query the directory.

## What is deployed

The migrations in `supabase/migrations/` are for Supabase PostgreSQL 15+. They model one listing for either an individual mechanic or a shop; there is no separate provider type or service category. They add no seed data and store no rider location, provider coordinates, exact street address, identity documents, or raw verification evidence.

Public directory access is limited to an explicitly published listing with a current verification window, recorded listing consent, recorded public-contact consent, a public phone number, and a matching current verification event. The event must match the provider's verification time and expiry. A later verification event that is not `verified` hides the listing immediately; future-dated or expired checks do not qualify. The public view runs with caller rights and exposes only `id`, `display_name`, `public_area_label`, `public_phone`, `verified_at`, `verification_valid_until`, and `updated_at`.

Public roles receive no provider write permissions. Provider enrollment, edits, and verification-event inserts are reserved for a trusted backend service role. The verification-event log is protected by RLS and the service role cannot update or delete events. Any privileged enrollment/moderation flow must run on a trusted server; never put a Supabase service-role key in the app or commit secrets.

## Checks performed

After applying both migrations, live database checks confirmed:

- `private.providers` has RLS enabled and contains **0 rows**; `private.provider_verification_events` has RLS enabled and contains **0 rows**.
- The public view has `security_invoker=true` and exactly the seven columns listed above.
- Anonymous clients can SELECT the public view but cannot insert provider records, read verification events, or read the internal `verification_status` column. Authenticated clients cannot update provider records.
- The service role can insert verification events but cannot update or delete them. The installed public read policy calls the current-verification event gate.

These checks verify installed schema, policy metadata, and grants. They do not test listing-filter behavior against records, perform an end-to-end REST request, or validate provider evidence. No sample or production rows were inserted as a test. Keep the `private` schema out of PostgREST's exposed-schema list and expose only the public `provider_directory` view.

## What remains before a live directory

The project and database boundary are set up, but **the live service is not ready**. The owner still needs an approved direct opt-in process or other permitted source for provider listings, explicit provider consent to display the listing and contact number, a documented verification and renewal standard, and an accountable operator to review and maintain provider records. No provider names, phone numbers, or locations have been gathered or contacted.

The Expo app is not wired to Supabase. The app must remain clearly demo-only until consented, verified listings are approved and end-to-end access rules are tested. Calls, messages, booking, payments, and dispatch remain out of scope until contact safety and operational support are resolved.

The Supabase project region is a data-location choice, not proof of legal or regulatory compliance. Confirm any applicable residency requirements before onboarding real provider data. The project creation estimate was $0/month, but re-check cost before any plan change or paid add-on; do not accept one without separate approval.

## Repository checks

`python3 tests/backend_contract_audit.py` is part of `npm test` and statically checks the SQL guardrails across both migrations. A static test does not replace live RLS/REST testing. The local type-check, web build, six mobile smoke groups, and accessibility audit passed on 2026-10-07; app screens and demo behavior were left unchanged.
