-- Patchlane verified provider directory foundation.
-- Target: Supabase-managed PostgreSQL 15+ (security_invoker views required).
-- No provider rows are seeded. Do not place rider coordinates or exact addresses here.

begin;

create schema if not exists private;
revoke all on schema private from public;
grant usage on schema private to anon, authenticated, service_role;

create table if not exists private.providers (
  id uuid primary key,
  display_name text not null check (length(btrim(display_name)) >= 2),
  public_area_label text not null check (length(btrim(public_area_label)) >= 2),
  public_phone text,
  publication_status text not null default 'draft'
    check (publication_status in ('draft', 'published', 'paused', 'removed')),
  verification_status text not null default 'pending'
    check (verification_status in ('pending', 'verified', 'rejected', 'expired')),
  verified_at timestamptz,
  verification_valid_until timestamptz,
  public_listing_consent_at timestamptz,
  public_listing_consent_version text,
  public_contact_consent_at timestamptz,
  public_contact_consent_version text,
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  constraint provider_verification_window_order
    check (verification_valid_until is null or verified_at is not null and verification_valid_until > verified_at),
  constraint provider_public_phone_format
    check (public_phone is null or public_phone ~ '^\+[1-9][0-9]{7,14}$')
);

create table if not exists private.provider_verification_events (
  id uuid primary key,
  provider_id uuid not null references private.providers(id) on delete restrict,
  reviewer_id uuid not null,
  verification_method text not null
    check (verification_method in ('phone_confirmation', 'business_record_check', 'in_person_check', 'other_documented')),
  outcome text not null check (outcome in ('verified', 'not_verified', 'needs_follow_up')),
  checked_at timestamptz not null default statement_timestamp(),
  valid_until timestamptz,
  constraint verification_event_window_order
    check (valid_until is null or valid_until > checked_at)
);

create index if not exists providers_area_lookup_idx
  on private.providers (lower(public_area_label), verification_status, publication_status);
create index if not exists provider_verification_events_provider_idx
  on private.provider_verification_events (provider_id, checked_at desc);

create or replace function private.guard_provider_publication()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := statement_timestamp();

  if new.publication_status = 'published' and (
    new.verification_status <> 'verified'
    or new.verified_at is null
    or new.verification_valid_until is null
    or new.verification_valid_until <= statement_timestamp()
    or new.public_listing_consent_at is null
    or nullif(btrim(new.public_listing_consent_version), '') is null
    or new.public_contact_consent_at is null
    or nullif(btrim(new.public_contact_consent_version), '') is null
    or new.public_phone is null
    or new.public_phone !~ '^\+[1-9][0-9]{7,14}$'
    or nullif(btrim(new.display_name), '') is null
    or nullif(btrim(new.public_area_label), '') is null
  ) then
    raise exception using
      errcode = '23514',
      message = 'Provider cannot be published without current verification and explicit listing/contact consent.';
  end if;

  return new;
end;
$$;

revoke all on function private.guard_provider_publication() from public, anon, authenticated;
create trigger providers_publication_guard
  before insert or update on private.providers
  for each row execute function private.guard_provider_publication();

alter table private.providers enable row level security;
create policy providers_public_directory_read
  on private.providers
  for select
  to anon, authenticated
  using (
    publication_status = 'published'
    and verification_status = 'verified'
    and verified_at is not null
    and verification_valid_until > statement_timestamp()
    and public_listing_consent_at is not null
    and nullif(btrim(public_listing_consent_version), '') is not null
    and public_contact_consent_at is not null
    and nullif(btrim(public_contact_consent_version), '') is not null
    and public_phone is not null
  );

-- Public clients may read only the approved directory fields. No public writes.
revoke all on private.providers, private.provider_verification_events from public, anon, authenticated;
grant select (id, display_name, public_area_label, public_phone, verified_at, verification_valid_until, updated_at)
  on private.providers to anon, authenticated;

grant select, insert, update, delete on private.providers, private.provider_verification_events to service_role;

-- security_invoker ensures the base table's column grants and RLS still apply.
create or replace view public.provider_directory
  with (security_invoker = true)
as
select
  id,
  display_name,
  public_area_label,
  public_phone,
  verified_at,
  verification_valid_until,
  updated_at
from private.providers
where publication_status = 'published'
  and verification_status = 'verified'
  and verified_at is not null
  and verification_valid_until > statement_timestamp()
  and public_listing_consent_at is not null
  and nullif(btrim(public_listing_consent_version), '') is not null
  and public_contact_consent_at is not null
  and nullif(btrim(public_contact_consent_version), '') is not null
  and public_phone is not null;

revoke all on public.provider_directory from public;
grant select on public.provider_directory to anon, authenticated;

revoke all on private.provider_verification_events from public, anon, authenticated;

commit;
