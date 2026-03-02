import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "lh3.googleusercontent.com" },   // Google
      { protocol: "https", hostname: "k.kakaocdn.net" },               // Kakao
      { protocol: "https", hostname: "ssl.pstatic.net" },              // Naver
      { protocol: "https", hostname: "phinf.pstatic.net" },            // Naver
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/static/**" }, // 로컬 dev mock
    ],
  },
};

export default nextConfig;
