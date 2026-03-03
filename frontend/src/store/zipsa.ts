import { create } from "zustand";
import { getProfile, getSessions, type UserProfileResponse, type ChatSession } from "@/lib/api";

interface ZipsaState {
  profile: UserProfileResponse | null;
  sessions: ChatSession[];

  setProfile: (profile: UserProfileResponse | null) => void;
  setSessions: (sessions: ChatSession[]) => void;
  addSession: (session: ChatSession) => void;
  removeSession: (sessionId: string) => void;
  updateSession: (sessionId: string, updates: Partial<ChatSession>) => void;
  reset: () => void;

  loadProfile: (token: string) => Promise<void>;
  loadSessions: (token: string) => Promise<void>;
}

export const useZipsaStore = create<ZipsaState>((set) => ({
  profile: null,
  sessions: [],

  setProfile: (profile) => set({ profile }),
  setSessions: (sessions) => set({ sessions }),
  reset: () => set({ profile: null, sessions: [] }),

  addSession: (session) =>
    set((state) => ({ sessions: [session, ...state.sessions] })),

  removeSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.session_id !== sessionId),
    })),

  updateSession: (sessionId, updates) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.session_id === sessionId ? { ...s, ...updates } : s,
      ),
    })),

  loadProfile: async (token) => {
    const profile = await getProfile(token);
    set({ profile });
  },

  loadSessions: async (token) => {
    const sessions = await getSessions(token);
    set({ sessions });
  },
}));
