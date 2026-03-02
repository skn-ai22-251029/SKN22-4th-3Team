/**
 * ZIPSA 백엔드 API 클라이언트
 *
 * ZIPSA JWT는 NextAuth 세션과 별도로 발급됨.
 * localStorage의 "zipsa_token" 키에 저장.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getZipsaToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("zipsa_token");
}

export function setZipsaToken(token: string): void {
  localStorage.setItem("zipsa_token", token);
}

export function clearZipsaToken(): void {
  localStorage.removeItem("zipsa_token");
}

// ── Auth ────────────────────────────────────────────────────────────────────

interface SyncRequest {
  email: string;
  name?: string | null;
  image?: string | null;
  provider: string;
}

interface SyncResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
}

export async function syncAuth(data: SyncRequest): Promise<SyncResponse> {
  const res = await fetch(`${API_BASE}/api/v1/auth/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`syncAuth failed: ${res.status}`);
  return res.json();
}

// ── Profile ─────────────────────────────────────────────────────────────────

export interface UserPreferences {
  housing: string;
  activity: string;
  experience: string;
  work_style?: string | null;
  allergy: boolean;
  has_children: boolean;
  has_dog: boolean;
  has_cat: boolean;
  traits: string[];
  companion: string[];
}

export interface UserProfileCreateRequest {
  nickname?: string | null;
  preferences: UserPreferences;
}

export interface UserProfileResponse {
  user_id: string;
  email: string;
  nickname?: string | null;
  age?: number | null;
  gender?: string | null;
  contact?: string | null;
  address?: string | null;
  avatar_url?: string | null;
  preferences: UserPreferences;
  onboarding_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdateRequest {
  nickname?: string | null;
  age?: number | null;
  gender?: string | null;
  contact?: string | null;
  address?: string | null;
  avatar_url?: string | null;
  preferences?: Partial<UserPreferences>;
}

export async function getProfile(token: string): Promise<UserProfileResponse> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw Object.assign(new Error("getProfile failed"), { status: res.status });
  return res.json();
}

export async function createProfile(
  token: string,
  data: UserProfileCreateRequest,
): Promise<UserProfileResponse> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/profile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw Object.assign(new Error(`createProfile failed: ${res.status}`), { status: res.status });
  return res.json();
}

export async function updateProfile(
  token: string,
  data: UserProfileUpdateRequest,
): Promise<UserProfileResponse> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`updateProfile failed: ${res.status}`);
  return res.json();
}

export async function getAvatarPresignUrl(
  token: string,
): Promise<{ upload_url: string; avatar_url: string }> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/profile/avatar/presign`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`getAvatarPresignUrl failed: ${res.status}`);
  return res.json();
}
