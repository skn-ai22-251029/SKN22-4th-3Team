"use client";

import { useEffect } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function AuthCallbackPage() {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/");
    } else if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [status, router]);

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center space-y-6">
        {/* Logo */}
        <h1 className="text-4xl font-bold text-gray-900">ZIPSA</h1>

        {/* Spinner */}
        <div className="flex justify-center">
          <Loader2 className="w-12 h-12 text-gray-400 animate-spin" strokeWidth={2} />
        </div>

        {/* Loading Text */}
        <p className="text-sm text-gray-500">로그인 중입니다...</p>
      </div>
    </div>
  );
}
