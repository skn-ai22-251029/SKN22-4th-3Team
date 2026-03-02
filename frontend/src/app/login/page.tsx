"use client";

import { signIn } from "next-auth/react";
import { Cat } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FcGoogle } from "react-icons/fc";
import { SiNaver } from "react-icons/si";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-white flex">
      {/* Left Half - Illustration */}
      <div className="w-1/2 bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <Cat className="w-48 h-48 text-gray-400 mx-auto" strokeWidth={1} />
          <p className="text-gray-500 text-sm mt-6">고양이 일러스트 영역</p>
        </div>
      </div>

      {/* Right Half - Login Card */}
      <div className="w-1/2 flex items-center justify-center px-8">
        <div className="w-full max-w-[400px] space-y-8">
          {/* Logo & Tagline */}
          <div className="text-center space-y-3">
            <h1 className="text-5xl font-bold text-gray-900">ZIPSA</h1>
            <p className="text-sm text-gray-500">
              나와 꼭 맞는 고양이를 찾아드려요.
            </p>
          </div>

          {/* Divider */}
          <div className="border-t-2 border-gray-300"></div>

          {/* SSO Buttons */}
          <div className="space-y-3">
            {/* Google Login */}
            <Button
              className="w-full h-[52px] bg-white border-2 border-gray-300 hover:bg-gray-50 text-gray-900 text-base flex items-center justify-center gap-3"
              onClick={() => signIn("google", { callbackUrl: "/auth/callback" })}
            >
              <FcGoogle className="w-5 h-5" />
              Google로 계속하기
            </Button>

            {/* Kakao Login */}
            <Button
              className="w-full h-[52px] bg-[#FEE500] border-2 border-[#FEE500] hover:bg-[#F5DC00] text-[#000000] text-[15px] font-medium flex items-center justify-center gap-3"
              onClick={() => signIn("kakao", { callbackUrl: "/auth/callback" })}
            >
              <svg
                viewBox="0 0 24 24"
                className="w-5 h-5"
                fill="currentColor"
              >
                <path d="M 12 3 A 10 7.882 0 0 0 4.34 15.94 L 3 21.5 L 8.58 18.28 A 10 7.882 0 0 0 12 18.764 A 10 7.882 0 0 0 22 10.882 A 10 7.882 0 0 0 12 3 Z" />
              </svg>
              카카오로 계속하기
            </Button>

            {/* Naver Login */}
            <Button
              className="w-full h-[52px] bg-[#03C75A] border-2 border-[#03C75A] hover:bg-[#02B350] text-white text-base flex items-center justify-center gap-3"
              onClick={() => signIn("naver", { callbackUrl: "/auth/callback" })}
            >
              <SiNaver className="w-5 h-5 text-white" />
              네이버로 계속하기
            </Button>
          </div>

          {/* Helper Text */}
          <p className="text-xs text-gray-500 text-center">
            처음 로그인하시면 간단한 설문 후 시작돼요.
          </p>

          {/* Terms */}
          <p className="text-[10px] text-gray-400 text-center leading-relaxed">
            로그인 시 서비스 이용약관 및 개인정보처리방침에 동의하는 것으로 간주합니다.
          </p>
        </div>
      </div>
    </div>
  );
}
