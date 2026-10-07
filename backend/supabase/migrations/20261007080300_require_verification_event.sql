-- Tighten publication after the initial directory deployment:
-- a published listing must match an append-only, current verification event.

begin;

create unique index if not exists provider_verification_events_provider_checked_at_uidx
  on private.provider_verification_events (provider_id, checked_at);

alter table private.provider_verification_events enable row level security;
revoke update, delete on private.provider_verification_events from service_role;
grant select, insert on private.provider_verification_events to service_role;

create or replace function private.has_current_provider_verification(
  p_provider_id uuid,
  p_verified_at timestamptz,
  p_valid_until timestamptz
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from private.provider_verification_events e
    where e.provider_id = p_provider_id
      and e.outcome = 'verified'
      and e.checked_at = p_verified_at
      and e.valid_until = p_valid_until
      and e.checked_at <= statement_timestamp()
      and e.valid_until > statement_timestamp()
      and not exists (
        select 1
        from private.provider_verification_events newer
        where newer.provider_id = e.provider_id
          and newer.checked_at > e.checked_at
      )
  );
$$;

revoke all on function private.has_current_provider_verification(uuid, timestamptz, timestamptz)
  from public, anon, authenticated, service_role;
grant execute on function private.has_current_provider_verification(uuid, timestamptz, timestamptz)
  to anon, authenticated, service_role;

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
    or new.verified_at > statement_timestamp()
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
    or not private.has_current_provider_verification(
      new.id,
      new.verified_at,
      new.verification_valid_until
    )
  ) then
    raise exception using
      errcode = '23514',
      message = 'Provider cannot be published without current verification, an audit event, and explicit listing/contact consent.';
  end if;

  return new;
end;
$$;

revoke all on function private.guard_provider_publication() from public, anon, authenticated;

-- Replace the read policy so a later failed/revoked check immediately hides the listing.
drop policy if exists providers_public_directory_read on private.providers;
create policy providers_public_directory_read
  on private.providers
  for select
  to anon, authenticated
  using (
    publication_status = 'published'
    and verification_status = 'verified'
    and verified_at is not null
    and verified_at <= statement_timestamp()
    and verification_valid_until > statement_timestamp()
    and public_listing_consent_at is not null
    and nullif(btrim(public_listing_consent_version), '') is not null
    and public_contact_consent_at is not null
    and nullif(btrim(public_contact_consent_version), '') is not null
    and public_phone is not null
    and private.has_current_provider_verification(id, verified_at, verification_valid_until)
  );

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
  and verified_at <= statement_timestamp()
  and verification_valid_until > statement_timestamp()
  and public_listing_consent_at is not null
  and nullif(btrim(public_listing_consent_version), '') is not null
  and public_contact_consent_at is not null
  and nullif(btrim(public_contact_consent_version), '') is not null
  and public_phone is not null
  and private.has_current_provider_verification(id, verified_at, verification_valid_until);

commit;
