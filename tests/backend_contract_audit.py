#!/usr/bin/env python3
"""Static regression checks for the deployed-but-empty provider-directory migration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "backend/supabase/migrations/20261007000000_verified_provider_directory.sql"
sql = MIGRATION.read_text(encoding="utf-8").lower()

required = {
    "row-level security is enabled": "alter table private.providers enable row level security",
    "public reads are restricted to anonymous/authenticated roles": "to anon, authenticated",
    "published listings must be verified": "verification_status = 'verified'",
    "verification must be current": "verification_valid_until > statement_timestamp()",
    "listing consent is required": "public_listing_consent_at is not null",
    "public contact consent is required": "public_contact_consent_at is not null",
    "consent wording versions are retained": "public_contact_consent_version",
    "public API view runs with caller privileges": "with (security_invoker = true)",
    "public view is read-only": "grant select on public.provider_directory to anon, authenticated",
    "anonymous writes are not granted": "grant select, insert, update, delete on private.providers, private.provider_verification_events to service_role",
    "publication is guarded on write": "create trigger providers_publication_guard",
    "verification history is retained separately": "create table if not exists private.provider_verification_events",
}

missing = [description for description, fragment in required.items() if fragment not in sql]
if missing:
    raise SystemExit("FAIL  missing migration guardrails: " + "; ".join(missing))

if r"'^\+[1-9][0-9]{7,14}$'" not in sql or r"'^\\+[1-9][0-9]{7,14}$'" in sql:
    raise SystemExit("FAIL  public phone validation must use the literal-plus E.164 pattern")

for forbidden in ("latitude", "longitude", "rider_location", "exact_address", "provider_type"):
    if forbidden in sql:
        raise SystemExit(f"FAIL  forbidden/minimization-sensitive field found in migration: {forbidden}")

if "insert into private.providers" in sql or "insert into private.provider_verification_events" in sql:
    raise SystemExit("FAIL  migration must not seed provider data or verification events")

print(f"PASS  backend contract static audit ({len(required) + 1} guardrails; no seeds or prohibited location/type fields)")
