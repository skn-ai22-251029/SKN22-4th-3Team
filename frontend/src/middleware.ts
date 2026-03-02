export { default } from "next-auth/middleware";

export const config = {
  // /login, /auth/*, /api/* 제외한 모든 경로 보호
  matcher: ["/((?!login|auth|api|_next/static|_next/image|favicon.ico).*)"],
};
