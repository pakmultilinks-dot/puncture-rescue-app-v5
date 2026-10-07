-- Keep the public directory readable through its invoker-rights view without
-- granting anonymous clients access to any columns on the private base table.
-- The SECURITY DEFINER accessor returns only the approved public fields and
-- repeats the full consent, expiry, and latest-verification gate.

begin;

create or replace function private.public_provider_directory_rows()
returns table (
  id uuid,
  display_name text,
  public_area_label text,
  public_phone text,
  verified_at timestamptz,
  verification_valid_until timestamptz,
  updated_at timestamptz
)
language sql
stable
security definer
set search_path = ''
as $function$
  select
    p.id,
    p.display_name,
    p.public_area_label,
    p.public_phone,
    p.verified_at,
    p.verification_valid_until,
    p.updated_at
  from private.providers as p
  where p.publication_status = 'published'
    and p.verification_status = 'verified'
    and p.verified_at is not null
    and p.verified_at <= pg_catalog.statement_timestamp()
    and p.verification_valid_until > pg_catalog.statement_timestamp()
    and p.public_listing_consent_at is not null
    and nullif(pg_catalog.btrim(p.public_listing_consent_version), '') is not null
    and p.public_contact_consent_at is not null
    and nullif(pg_catalog.btrim(p.public_contact_consent_version), '') is not null
    and p.public_phone is not null
    and private.has_current_provider_verification(
      p.id,
      p.verified_at,
      p.verification_valid_until
    )
  order by pg_catalog.lower(p.display_name), p.id;
$function$;

revoke all on function private.public_provider_directory_rows()
  from public, anon, authenticated, service_role;
grant execute on function private.public_provider_directory_rows()
  to anon, authenticated;

-- Remove the initial column-level grants: the API now reads only the safe
-- function result, and must not query private.providers directly.
revoke all on private.providers from public, anon, authenticated;
revoke select (
  id,
  display_name,
  public_area_label,
  public_phone,
  verified_at,
  verification_valid_until,
  updated_at
) on private.providers from public, anon, authenticated;

create or replace view public.provider_directory
  with (security_invoker = true, security_barrier = true)
as
select
  id,
  display_name,
  public_area_label,
  public_phone,
  verified_at,
  verification_valid_until,
  updated_at
from private.public_provider_directory_rows();

revoke all on public.provider_directory from public;
grant select on public.provider_directory to anon, authenticated;

commit;
