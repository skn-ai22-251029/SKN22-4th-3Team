export { default } from "next-auth/middleware";

export const config = {
  // 보호가 필요한 경로만 명시 (나머지는 public)
  matcher: ["/chat/:path*", "/onboarding/:path*", "/profile/:path*", "/my-cats/:path*", "/meme/:path*"],
};
