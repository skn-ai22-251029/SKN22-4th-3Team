"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ChatPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/chat/new");
  }, [router]);

  return (
    <div className="h-screen flex items-center justify-center bg-white">
      <p className="text-gray-400">대화를 준비하는 중...</p>
    </div>
  );
}
