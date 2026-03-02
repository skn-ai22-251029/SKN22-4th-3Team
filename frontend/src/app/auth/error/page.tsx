"use client";

import { useRouter } from "next/navigation";
import { XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AuthErrorPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-8">
      <div className="w-full max-w-[400px] space-y-6 text-center">
        {/* Error Icon */}
        <div className="flex justify-center">
          <XCircle className="w-12 h-12 text-gray-400" strokeWidth={2} />
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900">
          로그인에 실패했어요.
        </h1>

        {/* Description */}
        <p className="text-sm text-gray-500">
          잠시 후 다시 시도해주세요.
        </p>

        {/* Retry Button */}
        <Button
          className="w-full h-[52px] bg-gray-900 hover:bg-gray-800 text-white text-base rounded-lg"
          onClick={() => router.push("/login")}
        >
          다시 시도하기
        </Button>

        {/* Home Link */}
        <button
          className="text-sm text-gray-600 hover:text-gray-900 underline"
          onClick={() => router.push("/")}
        >
          홈으로 돌아가기
        </button>
      </div>
    </div>
  );
}
