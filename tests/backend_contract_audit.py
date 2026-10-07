#!/usr/bin/env python3
"""Static regression checks for the deployed, empty provider-directory migrations."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_DIR = ROOT / "backend/supabase/migrations"
migration_files = sorted(MIGRATION_DIR.glob("*.sql"))
if len(migration_files) < 2:
    raise SystemExit("FAIL  expected the base schema and verification-event hardening migrations")
sql = "\n".join(path.read_text(encoding="utf-8") for path in migration_files).lower()

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
    "publication requires a matching verification event": "or not private.has_current_provider_verification(",
    "directory reads require a current verification event": "and private.has_current_provider_verification(id, verified_at, verification_valid_until)",
    "verification events are append-only for service role": "revoke update, delete on private.provider_verification_events from service_role",
    "verification events are unique per provider/check time": "create unique index if not exists provider_verification_events_provider_checked_at_uidx",
    "verification-event table has RLS enabled": "alter table private.provider_verification_events enable row level security",
    "anonymous base-table access is revoked": "revoke all on private.providers from public, anon, authenticated",
    "directory reads pass through the public-fields accessor": "from private.public_provider_directory_rows()",
    "public invoker view is also a security barrier": "security_invoker = true, security_barrier = true",
}

missing = [description for description, fragment in required.items() if fragment not in sql]
if missing:
    raise SystemExit("FAIL  missing migration guardrails: " + "; ".join(missing))

accessor_start = sql.find("create or replace function private.public_provider_directory_rows()")
if accessor_start < 0:
    raise SystemExit("FAIL  missing the safe public provider accessor")
accessor_end = sql.find("$function$;", accessor_start)
accessor = sql[accessor_start:accessor_end if accessor_end >= 0 else None]
if "security definer" not in accessor or "set search_path = ''" not in accessor:
    raise SystemExit("FAIL  public accessor must be SECURITY DEFINER with an empty search_path")
for column in ("id uuid", "display_name text", "public_area_label text", "public_phone text", "verified_at timestamptz", "verification_valid_until timestamptz", "updated_at timestamptz"):
    if column not in accessor.split("language sql", 1)[0]:
        raise SystemExit(f"FAIL  public accessor return contract missing: {column}")
for gate in ("p.publication_status = 'published'", "p.verification_status = 'verified'", "p.public_listing_consent_at is not null", "p.public_contact_consent_at is not null", "and private.has_current_provider_verification("):
    if gate not in accessor:
        raise SystemExit(f"FAIL  public accessor is missing a visibility gate: {gate}")

if "grant select on private.providers to anon" in sql or "grant select on private.providers to authenticated" in sql:
    raise SystemExit("FAIL  public roles must not receive table-level provider SELECT")

if r"'^\+[1-9][0-9]{7,14}$'" not in sql or r"'^\\+[1-9][0-9]{7,14}$'" in sql:
    raise SystemExit("FAIL  public phone validation must use the literal-plus E.164 pattern")

for forbidden in ("latitude", "longitude", "rider_location", "exact_address", "provider_type"):
    if forbidden in sql:
        raise SystemExit(f"FAIL  forbidden/minimization-sensitive field found in migrations: {forbidden}")

if "insert into private.providers" in sql or "insert into private.provider_verification_events" in sql:
    raise SystemExit("FAIL  migrations must not seed provider data or verification events")

print(f"PASS  backend contract static audit ({len(required) + 1} guardrails; no seeds or prohibited location/type fields)")
