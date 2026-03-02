"use client";

import { useEffect, useRef } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { syncAuth, getProfile, setZipsaToken } from "@/lib/api";

export default function AuthCallbackPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const called = useRef(false);

  useEffect(() => {
    if (status !== "authenticated" || called.current) return;
    called.current = true;

    (async () => {
      try {
        const user = session!.user!;
        const provider =
          ((session as unknown as { user: { provider?: string } }).user?.provider ?? "unknown");

        // 1. ZIPSA JWT 발급
        const sync = await syncAuth({
          email: user.email!,
          name: user.name,
          image: user.image,
          provider,
        });
        setZipsaToken(sync.access_token);

        // 2. 프로필 존재 여부 확인
        try {
          await getProfile(sync.access_token);
          router.replace("/");
        } catch (err: unknown) {
          const status = (err as { status?: number }).status;
          if (status === 404) {
            router.replace("/onboarding");
          } else {
            router.replace("/");
          }
        }
      } catch {
        router.replace("/");
      }
    })();
  }, [status, session, router]);

  if (status === "unauthenticated") {
    router.replace("/login");
    return null;
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold text-gray-900">ZIPSA</h1>
        <div className="flex justify-center">
          <Loader2 className="w-12 h-12 text-gray-400 animate-spin" strokeWidth={2} />
        </div>
        <p className="text-sm text-gray-500">로그인 중입니다...</p>
      </div>
    </div>
  );
}
