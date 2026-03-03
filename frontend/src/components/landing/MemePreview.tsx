import Link from "next/link";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";

export function MemePreview() {
  return (
    <section className="w-full border-b border-gray-300 bg-white">
      <div className="max-w-[1440px] mx-auto px-16 py-20">
        <h2 className="text-3xl font-bold text-center mb-4 text-gray-900">
          냥심 번역기
        </h2>
        <p className="text-center text-gray-500 mb-16">
          고양이 사진을 올리면 AI가 고양이의 속마음을 대신 전해드립니다
        </p>

        <div className="grid grid-cols-2 gap-16 items-center max-w-[1000px] mx-auto">
          {/* Left — 업로드 영역 (정적) */}
          <div className="flex flex-col items-center">
            <div className="w-full aspect-square border-4 border-dashed border-gray-400 bg-white rounded-lg flex flex-col items-center justify-center select-none">
              <Upload className="w-12 h-12 text-gray-400 mb-4" strokeWidth={2} />
              <p className="text-gray-600 text-center px-8 leading-relaxed">
                고양이 사진을 드래그하거나<br />클릭해서 올려주세요
              </p>
            </div>

            <div className="w-full mt-6 border-2 border-gray-300 rounded-lg px-4 py-3 bg-white text-gray-400 text-sm select-none">
              한 마디 덧붙여 주세요 (선택사항, 예: 오늘 밥을 거부했어요)
            </div>

            <Link href="/meme" className="w-full mt-4">
              <Button className="w-full bg-gray-900 text-white hover:bg-gray-800 rounded-lg py-6 text-base font-medium">
                분석 시작하기
              </Button>
            </Link>
          </div>

          {/* Right — 폴라로이드 결과 (정적 목업) */}
          <div className="flex flex-col items-center">
            <div
              className="bg-white p-6 shadow-xl"
              style={{ transform: "rotate(2deg)", borderRadius: "4px" }}
            >
              <div className="w-[280px] h-[280px] bg-gray-100 border-2 border-gray-200 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-7xl mb-2">🐱</div>
                  <p className="text-gray-400 font-mono text-xs">CAT PHOTO</p>
                </div>
              </div>

              <div className="mt-5 px-2 space-y-3">
                <p className="text-gray-800 italic text-center leading-relaxed text-sm">
                  "인간아, 지금 당장 간식을<br />내놓지 않으면 후회할 거다냥"
                </p>
                <div className="flex justify-center gap-2">
                  <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                    코리안숏헤어
                  </span>
                  <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                    약 3살 추정
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-10">
              <Link href="/meme">
                <Button className="bg-gray-900 text-white hover:bg-gray-800 px-6">
                  내 고양이로 등록
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
