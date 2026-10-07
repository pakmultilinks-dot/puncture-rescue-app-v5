# Patchlane Supabase backend — schema deployed, app not connected

A separate Supabase project for the Lahore pilot is active and healthy in **Mumbai (`ap-south-1`)**. Supabase returned a project-creation estimate of **$0/month**; no paid upgrade was accepted. The project is not the existing FleetFlow project. The verified-provider directory migration is applied, but no provider rows or verification events exist, and the Expo app does not yet query the directory.

## What is deployed

`supabase/migrations/20261007000000_verified_provider_directory.sql` is a Supabase PostgreSQL 15+ migration. It models one listing for either an individual mechanic or a shop; there is no separate provider type or service category. It has no seed data and stores no rider location, provider coordinates, exact street address, identity documents, or raw verification evidence.

Public directory access is limited to an explicitly published listing with a current verification window, recorded listing consent, recorded public-contact consent, and a public phone number. The public view runs with caller rights and exposes only `id`, `display_name`, `public_area_label`, `public_phone`, `verified_at`, `verification_valid_until`, and `updated_at`. The public roles receive no provider write permissions. Provider enrollment, edits, and verification-event writes are reserved for a trusted backend service role. The listing guard rejects publication without current verification and both consent records; row-level security stops expired listings from being returned.

Provider verification events retain only the reviewer ID, check method, outcome, and validity window. Do not put raw identity documents, private notes, private phone numbers, or other sensitive evidence in these tables. Keep the source and proof needed to substantiate verification under a separately reviewed retention and access policy.

## Checks performed

After applying the migration, live database checks confirmed:

- `private.providers` has row-level security enabled and contains **0 rows**; `private.provider_verification_events` contains **0 rows**.
- The public view has `security_invoker=true` and exactly the seven columns listed above.
- The anonymous role can read the public view and its `public_phone` column, but cannot insert provider records or read verification events; the authenticated role cannot update provider records.
- The anonymous role cannot read the internal `verification_status` column.

These checks verify the installed schema, metadata and grants. They do not test positive/negative filter behavior with provider rows, perform an end-to-end REST request, or validate provider evidence. No sample or production rows were inserted as a test. Keep the `private` schema out of PostgREST's exposed-schema list and expose only the public `provider_directory` view.

## What remains before a live directory

The project and database boundary are set up, but **the live service is not ready**. The owner still needs an approved direct opt-in process or other permitted source for provider listings, explicit provider consent to display the listing and contact number, a documented verification and renewal standard, and an accountable operator to review and maintain provider records. No provider names, phone numbers, or locations have been gathered or contacted.

The Expo app is not wired to Supabase. Do not put a Supabase service-role key in the app or commit secrets. Any privileged enrollment/moderation flow must run on a trusted server. The app must remain clearly demo-only until consented, verified listings are approved and end-to-end access rules are tested. Calls, messages, booking, payments, and dispatch remain out of scope until contact safety and operational support are resolved.

The Supabase project region is a data-location choice, not proof of legal or regulatory compliance. Confirm any applicable residency requirements before onboarding real provider data. The project creation estimate was $0/month, but re-check cost before any plan change or paid add-on; do not accept one without separate approval.

## Repository checks

`python3 tests/backend_contract_audit.py` is part of `npm test` and statically checks the SQL guardrails. A static test does not replace live RLS/REST testing. The local type-check, web build, six mobile smoke groups, and accessibility audit passed on 2026-10-07; app screens and demo behavior were left unchanged.
