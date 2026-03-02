import type { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import type { OAuthConfig, OAuthUserConfig } from "next-auth/providers/oauth";

// Kakao 커스텀 OAuth2 프로바이더
function KakaoProvider(options: OAuthUserConfig<Record<string, unknown>>): OAuthConfig<Record<string, unknown>> {
  return {
    id: "kakao",
    name: "Kakao",
    type: "oauth",
    authorization: {
      url: "https://kauth.kakao.com/oauth/authorize",
      params: { scope: "profile_nickname profile_image account_email" },
    },
    token: {
      url: "https://kauth.kakao.com/oauth/token",
      async request({ params }) {
        const res = await fetch("https://kauth.kakao.com/oauth/token", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            grant_type: "authorization_code",
            client_id: options.clientId,
            client_secret: options.clientSecret,
            redirect_uri: params.redirect_uri as string,
            code: params.code as string,
          }).toString(),
        });
        const tokens = await res.json();
        return { tokens };
      },
    },
    userinfo: {
      url: "https://kapi.kakao.com/v2/user/me",
      async request({ tokens }) {
        const res = await fetch("https://kapi.kakao.com/v2/user/me", {
          headers: { Authorization: `Bearer ${tokens.access_token}` },
        });
        return res.json();
      },
    },
    profile(profile) {
      return {
        id: String(profile.id),
        name: (profile.kakao_account as Record<string, unknown>)?.profile
          ? ((profile.kakao_account as Record<string, Record<string, unknown>>).profile?.nickname as string)
          : String(profile.id),
        email: (profile.kakao_account as Record<string, unknown>)?.email as string | null ?? null,
        image: (profile.kakao_account as Record<string, Record<string, unknown>>)?.profile
          ?.thumbnail_image_url as string | null ?? null,
      };
    },
    ...options,
  };
}

// Naver 커스텀 OAuth2 프로바이더
function NaverProvider(options: OAuthUserConfig<Record<string, unknown>>): OAuthConfig<Record<string, unknown>> {
  return {
    id: "naver",
    name: "Naver",
    type: "oauth",
    authorization: {
      url: "https://nid.naver.com/oauth2.0/authorize",
      params: { scope: "" },
    },
    token: {
      url: "https://nid.naver.com/oauth2.0/token",
      async request({ params }) {
        const res = await fetch("https://nid.naver.com/oauth2.0/token", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            grant_type: "authorization_code",
            client_id: options.clientId,
            client_secret: options.clientSecret,
            redirect_uri: params.redirect_uri as string,
            code: params.code as string,
          }).toString(),
        });
        const tokens = await res.json();
        return { tokens };
      },
    },
    userinfo: {
      url: "https://openapi.naver.com/v1/nid/me",
      async request({ tokens }) {
        const res = await fetch("https://openapi.naver.com/v1/nid/me", {
          headers: { Authorization: `Bearer ${tokens.access_token}` },
        });
        return res.json();
      },
    },
    profile(profile) {
      const resp = profile.response as Record<string, string>;
      return {
        id: resp.id,
        name: resp.name ?? resp.nickname ?? resp.id,
        email: resp.email ?? null,
        image: resp.profile_image ?? null,
      };
    },
    ...options,
  };
}

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    KakaoProvider({
      clientId: process.env.KAKAO_CLIENT_ID!,
      clientSecret: process.env.KAKAO_CLIENT_SECRET!,
    }),
    NaverProvider({
      clientId: process.env.NAVER_CLIENT_ID!,
      clientSecret: process.env.NAVER_CLIENT_SECRET!,
    }),
  ],
  pages: {
    signIn: "/login",
    error: "/auth/error",
  },
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account) {
        token.provider = account.provider;
        token.providerAccountId = account.providerAccountId;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as Record<string, unknown>).provider = token.provider;
      }
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
};
