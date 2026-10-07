export type ProviderDirectoryRecord = {
  id: string;
  display_name: string;
  public_area_label: string;
  public_phone: string;
  verified_at: string;
  verification_valid_until: string;
  updated_at: string;
};

// Expo inlines only these explicitly public client settings at bundle time.
// Never add a Supabase service-role key to this module or the mobile app.
declare const process: {
  env: {
    EXPO_PUBLIC_SUPABASE_URL?: string;
    EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY?: string;
  };
};

const SUPABASE_URL = (process.env.EXPO_PUBLIC_SUPABASE_URL ?? '').replace(/\/+$/, '');
const PUBLISHABLE_KEY = process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? '';
const PUBLIC_FIELDS = 'id,display_name,public_area_label,public_phone,verified_at,verification_valid_until,updated_at';

export const isProviderDirectoryConfigured = Boolean(SUPABASE_URL && PUBLISHABLE_KEY);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function toPublicRecord(value: unknown): ProviderDirectoryRecord | null {
  if (!isRecord(value)) return null;
  const { id, display_name, public_area_label, public_phone, verified_at, verification_valid_until, updated_at } = value;
  if (
    typeof id !== 'string' || id.length < 8 ||
    typeof display_name !== 'string' || display_name.trim().length < 2 ||
    typeof public_area_label !== 'string' || public_area_label.trim().length < 2 ||
    typeof public_phone !== 'string' || !/^\+[1-9][0-9]{7,14}$/.test(public_phone) ||
    typeof verified_at !== 'string' || !Number.isFinite(Date.parse(verified_at)) ||
    typeof verification_valid_until !== 'string' || !Number.isFinite(Date.parse(verification_valid_until)) ||
    typeof updated_at !== 'string' || !Number.isFinite(Date.parse(updated_at))
  ) return null;
  return {
    id,
    display_name: display_name.trim(),
    public_area_label: public_area_label.trim(),
    public_phone,
    verified_at,
    verification_valid_until,
    updated_at,
  };
}

export async function searchProviderDirectory(area: string, signal?: AbortSignal): Promise<ProviderDirectoryRecord[]> {
  if (!isProviderDirectoryConfigured) throw new Error('The live provider directory is not configured.');
  const searchText = area.trim()
    .replace(/[,*%()"\\]/g, ' ')
    .replace(/\s+/g, ' ')
    .slice(0, 80);
  if (searchText.length < 2) return [];

  const query = new URLSearchParams({
    select: PUBLIC_FIELDS,
    public_area_label: `ilike.*${searchText}*`,
    order: 'display_name.asc',
    limit: '50',
  });
  const response = await fetch(`${SUPABASE_URL}/rest/v1/provider_directory?${query.toString()}`, {
    method: 'GET',
    headers: {
      apikey: PUBLISHABLE_KEY,
      Accept: 'application/json',
    },
    signal,
  });
  if (!response.ok) throw new Error('The live provider directory could not be reached.');

  const payload: unknown = await response.json();
  if (!Array.isArray(payload)) throw new Error('The live provider directory returned an invalid response.');
  return payload.map(toPublicRecord).filter((record): record is ProviderDirectoryRecord => record !== null);
}
