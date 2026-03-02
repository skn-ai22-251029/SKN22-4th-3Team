"use client";

import { Cat } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Recommendation } from "@/lib/api";

interface CatCardProps {
  breed: Recommendation;
}

export function CatCard({ breed }: CatCardProps) {
  return (
    <div className="border-2 border-gray-300 bg-white shadow-md rounded-lg overflow-hidden">
      <div className="w-full h-[360px] bg-gray-200 border-b-2 border-gray-300 overflow-hidden flex items-center justify-center">
        {breed.image_url ? (
          <img
            src={breed.image_url}
            alt={breed.name_ko}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-center">
            <Cat className="w-16 h-16 text-gray-400 mx-auto mb-2" strokeWidth={1} />
            <p className="text-gray-400 font-mono text-xs">BREED IMAGE</p>
          </div>
        )}
      </div>

      <div className="p-5 space-y-3">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{breed.name_ko}</h3>
          <p className="text-sm text-gray-500 mt-1">{breed.name_en}</p>
        </div>

        {breed.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {breed.tags.map((tag, i) => (
              <Badge
                key={i}
                variant="outline"
                className="border-2 border-gray-400 text-gray-700 rounded-full px-3 py-1 text-xs"
              >
                {tag}
              </Badge>
            ))}
          </div>
        )}

        <div className="h-[2px] bg-gray-300" />

        <p className="text-sm text-gray-700 leading-relaxed">{breed.summary}</p>
      </div>
    </div>
  );
}
