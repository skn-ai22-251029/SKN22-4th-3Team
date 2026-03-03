"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CatCard } from "@/components/chat/CatCard";
import { RescueCatCard } from "@/components/chat/RescueCatCard";
import type { Recommendation, RescueCat } from "@/lib/api";

// ── 시나리오별 목업 데이터 ────────────────────────────────────────────────────

const breedScenario: {
  messages: { role: "human" | "ai"; content: string }[];
  breed: Recommendation;
} = {
  messages: [
    {
      role: "human",
      content: "1인 가구인데 조용하고 순한 고양이를 찾고 있어요. 혼자 있는 시간이 많아요.",
    },
    {
      role: "ai",
      content:
        "집사님의 환경에 딱 맞는 래그돌을 추천드릴게요! 인형처럼 온순하고, 혼자 있는 시간도 잘 견디며 조용한 성격이라 1인 가구에 최적입니다.",
    },
  ],
  breed: {
    name_ko: "래그돌",
    name_en: "Ragdoll",
    image_url: "",
    summary:
      "인형처럼 축 늘어지는 대형묘로 극도로 온순합니다. 조용하고 순종적이며, 혼자 있는 시간도 잘 견뎌 1인 가구에 잘 어울립니다.",
    tags: ["온순함", "조용함", "친화적", "실내 적합"],
    stats: {},
  },
};

const rescueScenario: {
  messages: { role: "human" | "ai"; content: string }[];
  cat: RescueCat;
} = {
  messages: [
    {
      role: "human",
      content: "직접 입양하고 싶은데, 지금 보호 중인 고양이가 있나요?",
    },
    {
      role: "ai",
      content:
        "국가동물보호정보시스템에서 입양 가능한 아이를 찾아왔어요! 온순하고 건강상태도 양호해요.",
    },
  ],
  cat: {
    animal_id: "DEMO001",
    breed: "코리안숏헤어",
    age: "2살 추정",
    sex: "여",
    neutered: "중성화 완료",
    feature: "온순하고 사람을 잘 따릅니다. 건강상태 양호, 기본 접종 완료.",
    image_url: "",
    shelter_name: "서울특별시 동물보호센터",
    shelter_address: "서울시 마포구 상암동",
    shelter_phone: "02-000-0000",
    notice_end_date: "2026-03-31",
    sido: "서울",
    sigungu: "마포구",
  },
};

// ── 컴포넌트 ─────────────────────────────────────────────────────────────────

export function DemoSection() {
  const [tab, setTab] = useState<"breed" | "rescue">("breed");

  const scenario = tab === "breed" ? breedScenario : rescueScenario;

  return (
    <section className="w-full border-b border-gray-300 bg-gray-100">
      <div className="max-w-[1440px] mx-auto px-16 py-20">
        <h2 className="text-3xl font-bold text-center mb-4 text-gray-900">
          이렇게 대화해요
        </h2>
        <p className="text-center text-gray-500 mb-12">
          AI 집사와 나눈 대화 한 마디로, 맞춤 품종 추천부터 입양 정보까지 바로 확인할 수 있어요.
        </p>

        {/* 시나리오 탭 */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex border-2 border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setTab("breed")}
              className={`px-6 py-2.5 text-sm font-medium transition-colors ${
                tab === "breed"
                  ? "bg-gray-900 text-white"
                  : "bg-white text-gray-600 hover:bg-gray-100"
              }`}
            >
              품종 추천
            </button>
            <button
              onClick={() => setTab("rescue")}
              className={`px-6 py-2.5 text-sm font-medium transition-colors border-l-2 border-gray-300 ${
                tab === "rescue"
                  ? "bg-gray-900 text-white"
                  : "bg-white text-gray-600 hover:bg-gray-100"
              }`}
            >
              구조묘 입양
            </button>
          </div>
        </div>

        {/* 채팅 UI 미리보기 */}
        <div className="border-2 border-gray-300 rounded-xl overflow-hidden flex h-[520px] shadow-sm">

          {/* 좌측: 채팅 영역 */}
          <div className="flex-1 flex flex-col border-r-2 border-gray-300">
            {/* 헤더 */}
            <div className="h-14 px-5 border-b-2 border-gray-300 flex items-center gap-3 bg-white flex-shrink-0">
              <div className="w-7 h-7 rounded-full bg-gray-900 flex items-center justify-center">
                <span className="text-white text-xs font-bold">Z</span>
              </div>
              <span className="text-sm font-bold text-gray-900">ZIPSA 집사</span>
            </div>

            {/* 메시지 */}
            <div className="flex-1 p-5 space-y-4 overflow-y-auto bg-gray-100">
              {scenario.messages.map((msg, i) =>
                msg.role === "human" ? (
                  <div key={i} className="flex justify-end">
                    <div className="bg-gray-200 border-2 border-gray-300 rounded-2xl px-4 py-3 max-w-sm">
                      <p className="text-gray-900 text-sm leading-relaxed">{msg.content}</p>
                    </div>
                  </div>
                ) : (
                  <div key={i} className="flex justify-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-white text-xs font-bold">Z</span>
                    </div>
                    <div className="bg-white border-2 border-gray-300 rounded-2xl px-4 py-3 max-w-sm">
                      <p className="text-gray-900 text-sm leading-relaxed">{msg.content}</p>
                    </div>
                  </div>
                )
              )}
            </div>

            {/* 입력창 (비활성) */}
            <div className="border-t-2 border-gray-300 p-4 bg-white flex-shrink-0">
              <div className="flex gap-2">
                <div className="flex-1 h-10 border-2 border-gray-200 rounded-lg px-4 flex items-center">
                  <span className="text-gray-400 text-sm">메시지를 입력하세요...</span>
                </div>
                <Link href="/chat">
                  <Button className="h-10 bg-gray-900 text-white hover:bg-gray-800 px-4">
                    시작하기
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* 우측: 카드 패널 */}
          <div className="w-[340px] flex flex-col bg-gray-100 flex-shrink-0">
            <div className="h-14 px-5 border-b-2 border-gray-300 flex items-center bg-white flex-shrink-0">
              <span className="text-sm font-bold text-gray-900">
                {tab === "breed" ? "추천 품종" : "구조묘 정보"}
              </span>
            </div>
            <div className="flex-1 p-4 overflow-y-auto">
              {tab === "breed" ? (
                <CatCard breed={breedScenario.breed} />
              ) : (
                <RescueCatCard cat={rescueScenario.cat} />
              )}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-10">
          <Link href="/chat">
            <Button
              size="lg"
              className="bg-gray-900 hover:bg-gray-800 text-white px-10 py-6 text-base"
            >
              나와 맞는 고양이 찾아보기
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
