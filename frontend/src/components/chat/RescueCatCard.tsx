"use client";

import { Cat } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { RescueCat } from "@/lib/api";

interface RescueCatCardProps {
  cat: RescueCat;
}

export function RescueCatCard({ cat }: RescueCatCardProps) {
  return (
    <div className="border-2 border-gray-300 bg-white shadow-md rounded-lg overflow-hidden">
      {/* 이미지 */}
      <div className="relative w-full h-[280px] bg-gray-200 border-b-2 border-gray-300 overflow-hidden flex items-center justify-center">
        {cat.image_url ? (
          <img
            src={cat.image_url}
            alt={cat.breed || "구조묘"}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-center">
            <Cat className="w-16 h-16 text-gray-400 mx-auto mb-2" strokeWidth={1} />
            <p className="text-gray-400 font-mono text-xs">CAT IMAGE</p>
          </div>
        )}
        <div className="absolute top-3 left-3">
          <Badge className="bg-gray-900 text-white border-0 rounded-full px-3 py-1 text-xs">
            입양 가능
          </Badge>
        </div>
      </div>

      {/* 카드 바디 */}
      <div className="p-5 space-y-3">
        {/* 품종 */}
        <div>
          <h3 className="text-xl font-bold text-gray-900">{cat.breed || "품종 미상"}</h3>
        </div>

        {/* 정보 태그: 나이, 성별, 중성화 */}
        <div className="flex flex-wrap gap-2">
          {cat.age && (
            <Badge variant="outline" className="border-2 border-gray-400 text-gray-700 rounded-full px-3 py-1 text-xs">
              {cat.age}
            </Badge>
          )}
          {cat.sex && (
            <Badge variant="outline" className="border-2 border-gray-400 text-gray-700 rounded-full px-3 py-1 text-xs">
              {cat.sex}
            </Badge>
          )}
          {cat.neutered && cat.neutered !== "미상" && (
            <Badge variant="outline" className="border-2 border-gray-400 text-gray-700 rounded-full px-3 py-1 text-xs">
              {cat.neutered}
            </Badge>
          )}
        </div>

        <div className="h-[2px] bg-gray-300" />

        {/* 특이사항 */}
        {cat.feature && (
          <p className="text-sm text-gray-700 leading-relaxed">{cat.feature}</p>
        )}

        {/* 보호소 정보 */}
        <div className="space-y-1">
          {cat.shelter_name && (
            <p className="text-sm font-medium text-gray-900">{cat.shelter_name}</p>
          )}
          {cat.shelter_address && (
            <p className="text-xs text-gray-500">{cat.shelter_address}</p>
          )}
          {cat.notice_end_date && (
            <p className="text-xs text-gray-400">공고 마감: {cat.notice_end_date}</p>
          )}
        </div>

        {/* 입양 문의 버튼 */}
        {cat.shelter_phone ? (
          <a
            href={`tel:${cat.shelter_phone}`}
            className="block w-full bg-gray-900 text-white text-sm font-medium text-center py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
          >
            입양 문의하기 ({cat.shelter_phone})
          </a>
        ) : (
          <button
            disabled
            className="w-full bg-gray-300 text-gray-500 text-sm font-medium py-2.5 rounded-lg cursor-not-allowed"
          >
            입양 문의하기
          </button>
        )}
      </div>
    </div>
  );
}
