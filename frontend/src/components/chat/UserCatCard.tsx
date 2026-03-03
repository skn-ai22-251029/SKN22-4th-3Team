"use client";

import { Cat } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { UserCat } from "@/lib/api";

interface UserCatCardProps {
  cat: UserCat;
  onEdit?: () => void;
}

function formatAge(months: number): string {
  const years = Math.floor(months / 12);
  const rem = months % 12;
  if (years > 0 && rem > 0) return `${years}살 ${rem}개월`;
  if (years > 0) return `${years}살`;
  return `${rem}개월`;
}

function genderLabel(g: string): string {
  if (g === "M") return "수컷";
  if (g === "F") return "암컷";
  return g;
}

export function UserCatCard({ cat, onEdit }: UserCatCardProps) {
  const lastVaccination = cat.health?.vaccinations?.[cat.health.vaccinations.length - 1];

  return (
    <div className="border-2 border-gray-300 rounded-lg p-6 bg-white space-y-4">
      {/* 이미지 플레이스홀더 */}
      <div className="flex justify-center">
        <div className="w-24 h-24 rounded-full bg-gray-200 border-2 border-gray-300 overflow-hidden flex items-center justify-center">
          {cat.profile_image_url ? (
            <img
              src={cat.profile_image_url}
              alt={cat.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <Cat className="w-12 h-12 text-gray-400" strokeWidth={1} />
          )}
        </div>
      </div>

      {/* 이름 + 품종 + 나이 */}
      <div className="text-center space-y-2">
        <h3 className="text-xl font-bold text-gray-900">{cat.name}</h3>
        <p className="text-sm text-gray-600">
          {cat.breed_name_ko || "품종 미상"} · {formatAge(cat.age_months)}
        </p>

        {/* 성별 */}
        {cat.gender && cat.gender !== "미상" && (
          <div className="flex justify-center">
            <Badge
              variant="outline"
              className="border-2 border-gray-400 rounded-full px-3 py-1 text-xs text-gray-700"
            >
              {genderLabel(cat.gender)}
            </Badge>
          </div>
        )}

        {/* 냥심 한 마디 */}
        {cat.meme_text && (
          <p className="text-xs text-gray-500 italic border-t-2 border-gray-100 pt-2">
            {cat.meme_text}
          </p>
        )}

        {/* 접종 정보 */}
        {lastVaccination && (
          <div className="pt-2 border-t-2 border-gray-200">
            <p className="text-xs text-gray-500">{lastVaccination.label}</p>
            <p className="text-xs text-gray-400">{lastVaccination.date}</p>
          </div>
        )}
      </div>

      {/* 수정 버튼 */}
      <Button
        variant="outline"
        className="w-full border-2 border-gray-900 bg-white text-gray-900 hover:bg-gray-100 text-sm"
        onClick={onEdit}
      >
        수정하기
      </Button>
    </div>
  );
}
