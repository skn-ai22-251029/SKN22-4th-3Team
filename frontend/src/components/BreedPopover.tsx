"use client";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";

interface BreedPopoverProps {
  triggerText: string;
  breedKorean: string;
  breedEnglish: string;
  tags: string[];
  summary: string;
  onViewDetails?: () => void;
}

export function BreedPopover({
  triggerText,
  breedKorean,
  breedEnglish,
  tags,
  summary,
  onViewDetails,
}: BreedPopoverProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <span className="underline decoration-2 decoration-gray-400 cursor-pointer hover:decoration-gray-600 transition-colors">
          {triggerText}
        </span>
      </PopoverTrigger>
      <PopoverContent
        className="w-[280px] p-3 border-2 border-gray-300 bg-white shadow-lg relative"
        side="top"
        sideOffset={8}
      >
        <div className="space-y-2">
          <div className="flex gap-3">
            <div className="w-[60px] h-[60px] rounded bg-gray-200 border-2 border-gray-300 flex items-center justify-center flex-shrink-0">
              <span className="text-2xl">🐱</span>
            </div>
            <div className="flex flex-col justify-center min-w-0">
              <h4 className="font-bold text-gray-900 text-sm leading-tight">{breedKorean}</h4>
              <p className="text-xs text-gray-500 mt-0.5">{breedEnglish}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {tags.map((tag, index) => (
              <Badge
                key={index}
                variant="outline"
                className="border-gray-400 text-gray-700 rounded-full px-2 py-0.5 text-xs"
              >
                {tag}
              </Badge>
            ))}
          </div>
          <p className="text-xs text-gray-700 leading-relaxed line-clamp-1">{summary}</p>
          <div className="flex justify-end">
            <button
              onClick={onViewDetails}
              className="text-xs text-gray-600 underline hover:text-gray-900 transition-colors"
            >
              자세히 보기
            </button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
