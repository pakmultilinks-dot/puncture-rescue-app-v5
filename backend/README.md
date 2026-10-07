# Patchlane backend foundation (not deployed)

This is the first database boundary for a real provider directory, not a running backend. The app still uses its clearly marked fictional examples. There are no provider records, accounts, requests, messages, or live contact actions in this migration.

## What the migration establishes

`supabase/migrations/20261007000000_verified_provider_directory.sql` is a Supabase-compatible PostgreSQL 15+ starting point. It models one provider listing for either an individual mechanic or a shop; there is no separate provider type or service category. It has no seed data and stores no rider location, provider coordinates, exact street address, identity documents, or verification evidence.

Public directory access is limited to an explicitly published listing with a current verification window, recorded listing consent, recorded public-contact consent, and a public phone number. The public role can read only the display name, coarse area label, consented public phone, verification dates, and update time. Anonymous clients cannot write provider records or verification events. The listing guard rejects attempts to publish incomplete or expired records, and the RLS policy stops listings from being returned when verification expires.

Provider verification events retain only the reviewer, check method, outcome, and validity window. Do not put raw identity documents, private notes, private phone numbers, or other sensitive evidence in these tables. Store only the evidence needed to substantiate verification, under a separately reviewed retention and access policy.

## Not yet configured

No Supabase project is connected or provisioned, and this migration has not been run against a database. The current Expo client has not been wired to the directory endpoint. Do not put a Supabase service-role key in the app; any privileged enrollment or moderation flow must run on a trusted server.

Before deployment, the owner needs to choose:

1. The launch city/coverage area and the data-hosting region that satisfies local requirements.
2. Supabase (the prepared reference target) or a different backend.
3. A Supabase project/account and an authorized deployment path, if Supabase is selected.
4. The provider-verification standard, consent wording/retention rules, and an accountable person who can review listings and keep verification current.
5. A permitted source or direct opt-in process for provider records. Do not scrape private contact details, add names or phone numbers without provider permission, or publish sample/demo records.

The existing app must remain in demo mode until the backend is actually deployed, real provider information has been verified and consented, and operational support and contact-safety decisions are settled. Calls, messages, booking, payments, and dispatch are deliberately outside this foundation.

## Deployment and checks

After the owner selects Supabase and provides project access through an approved connector, review the project's region and API exposure settings, then apply the migration using the project's authorized Supabase CLI workflow. Keep the `private` schema out of PostgREST's exposed-schema list; expose only the public `provider_directory` view. Verify with the anonymous key that unverified, expired, unconsented, paused, and removed records are not returned, and verify that anonymous inserts/updates fail. Do not add production records as a deployment test.

The migration's static regression check is `python3 tests/backend_contract_audit.py`. It validates key guardrails in the SQL source, but is not a substitute for running the migration and testing RLS in a provisioned PostgreSQL project.
