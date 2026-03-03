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

// ── Chat ─────────────────────────────────────────────────────────────────────

export interface Recommendation {
  name_ko: string;
  name_en: string;
  image_url: string;
  summary: string;
  tags: string[];
  stats: Record<string, number>;
}

export interface RagDoc {
  title: string;
  subtitle: string;
  source: string;
  url: string;
}

export interface ChatSession {
  session_id: string;
  user_id: string;
  thread_id: string;
  title: string;
  last_message: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface RescueCat {
  animal_id: string;
  breed: string;
  age: string;
  sex: string;
  neutered: string;
  feature: string;
  image_url: string;
  shelter_name: string;
  shelter_address: string;
  shelter_phone: string;
  notice_end_date: string;
  sido: string;
  sigungu: string;
}

export interface ChatMessage {
  message_id: string;
  session_id: string;
  role: "human" | "ai";
  content: string;
  recommendations: Recommendation[];
  rag_docs: RagDoc[];
  rescue_cats: RescueCat[];
  created_at: string;
}

export async function createSession(token: string): Promise<ChatSession> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error(`createSession failed: ${res.status}`);
  return res.json();
}

export async function getSessions(token: string): Promise<ChatSession[]> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/sessions`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`getSessions failed: ${res.status}`);
  return res.json();
}

export async function deleteSession(token: string, sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/sessions/${sessionId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`deleteSession failed: ${res.status}`);
}

export async function getMessages(token: string, sessionId: string): Promise<ChatMessage[]> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/sessions/${sessionId}/messages`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`getMessages failed: ${res.status}`);
  return res.json();
}

// ── UserCat ──────────────────────────────────────────────────────────────────

export interface VaccinationInfo {
  label: string;
  date: string;
}

export interface UserCatHealth {
  vaccinations: VaccinationInfo[];
}

export interface UserCat {
  cat_id: string;
  user_id: string;
  name: string;
  age_months: number;
  gender: string;
  breed_name_ko: string;
  breed_name_en: string;
  profile_image_url: string | null;
  meme_text: string | null;
  health: UserCatHealth;
  created_at: string;
  updated_at: string;
}

export interface UserCatCreateRequest {
  name: string;
  age_months?: number;
  gender?: string;
  breed_name_ko?: string;
  breed_name_en?: string;
  profile_image_url?: string | null;
  meme_text?: string | null;
  health?: Partial<UserCatHealth>;
}

export interface UserCatUpdateRequest {
  name?: string;
  age_months?: number;
  gender?: string;
  breed_name_ko?: string;
  breed_name_en?: string;
  profile_image_url?: string | null;
  meme_text?: string | null;
  health?: Partial<UserCatHealth>;
}

export async function uploadCatImage(token: string, image: File): Promise<{ image_url: string }> {
  const form = new FormData();
  form.append("image", image);
  const res = await fetch(`${API_BASE}/api/v1/users/me/cats/upload-image`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  if (!res.ok) throw new Error(`uploadCatImage failed: ${res.status}`);
  return res.json();
}

export async function getUserCats(token: string): Promise<UserCat[]> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/cats`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`getUserCats failed: ${res.status}`);
  return res.json();
}

export async function createUserCat(token: string, data: UserCatCreateRequest): Promise<UserCat> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/cats`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`createUserCat failed: ${res.status}`);
  return res.json();
}

export async function updateUserCat(
  token: string,
  catId: string,
  data: UserCatUpdateRequest,
): Promise<UserCat> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/cats/${catId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`updateUserCat failed: ${res.status}`);
  return res.json();
}

// ── Meme ─────────────────────────────────────────────────────────────────────

export interface MemeAnalyzeResponse {
  meme_text: string;
  breed_guess: string;
  age_guess: string;
  age_months: number;
  image_url: string;
}

export async function analyzeMeme(
  token: string,
  image: File,
  context: string,
): Promise<MemeAnalyzeResponse> {
  const form = new FormData();
  form.append("image", image);
  form.append("context", context);
  const res = await fetch(`${API_BASE}/api/v1/meme/analyze`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  if (!res.ok) throw new Error(`analyzeMeme failed: ${res.status}`);
  return res.json();
}

export async function deleteUserCat(token: string, catId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/users/me/cats/${catId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`deleteUserCat failed: ${res.status}`);
}

export async function* streamChat(
  token: string,
  sessionId: string,
  message: string,
  userProfile?: UserProfileResponse | null,
): AsyncGenerator<
  | { type: "token"; content: string }
  | { type: "recommendations"; data: Recommendation[] }
  | { type: "rag_docs"; data: RagDoc[] }
  | { type: "rescue_cats"; data: RescueCat[] }
  | { type: "error"; content: string }
  | { type: string; content?: string; data?: unknown }
> {
  const res = await fetch(`${API_BASE}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ session_id: sessionId, message, user_profile: userProfile ?? null }),
  });
  if (!res.ok) throw new Error(`streamChat failed: ${res.status}`);
  if (!res.body) return;

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = line.slice(6);
      if (payload === "[DONE]") return;
      try { yield JSON.parse(payload); } catch { /* skip malformed */ }
    }
  }
}
