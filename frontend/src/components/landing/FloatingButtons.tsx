"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowUp } from "lucide-react";

export function FloatingButtons() {
  const [showTop, setShowTop] = useState(false);

  useEffect(() => {
    const onScroll = () => setShowTop(window.scrollY > 300);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="fixed bottom-8 right-8 flex flex-col gap-3 z-50">
      <Link
        href="/meme"
        className="w-14 h-14 rounded-full bg-amber-400 hover:bg-amber-500 text-gray-900 flex flex-col items-center justify-center transition-colors gap-0.5"
        style={{ boxShadow: "0 8px 24px rgba(251,191,36,0.5)" }}
        title="냥심 번역기"
      >
        <span className="text-lg leading-none">🐱</span>
        <span className="text-[9px] font-bold leading-none">냥심번역기</span>
      </Link>

      {showTop && (
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="w-14 h-14 rounded-full bg-white hover:bg-gray-50 text-gray-900 flex items-center justify-center transition-colors border border-gray-200"
          style={{ boxShadow: "0 8px 24px rgba(0,0,0,0.15)" }}
          title="맨 위로"
        >
          <ArrowUp className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}
