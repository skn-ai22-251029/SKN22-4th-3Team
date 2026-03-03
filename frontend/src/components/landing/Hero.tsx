import { Button } from "@/components/ui/button";
import Link from "next/link";

export function Hero() {
  return (
    <section className="w-full border-b border-gray-300 bg-white" style={{ minHeight: "600px" }}>
      <div className="max-w-[1440px] mx-auto px-16 py-20">
        <div className="grid grid-cols-2 gap-16 items-center">
          <div className="space-y-6">
            <div className="inline-block border-2 border-gray-300 rounded-full px-4 py-1 bg-gray-50">
              <span className="text-sm font-medium text-gray-700">AI 파트너 서비스</span>
            </div>
            <h1 className="text-5xl font-bold text-gray-900 leading-tight">
              완벽한 집사가 되는 길,<br />당신 곁에는 가장 스마트한<br />AI 파트너가 있습니다.
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              라이프스타일 분석으로 찾는 최적의 입양부터 정밀 건강 케어까지,<br />
              AI 전문가 팀의 데이터가 당신의 반려 생활을 지원합니다.
            </p>
            <div className="flex gap-4 pt-2">
              <div className="border-2 border-gray-300 rounded-lg px-4 py-2 bg-white">
                <p className="text-sm font-bold text-gray-900">67종 품종 추천</p>
              </div>
              <div className="border-2 border-gray-300 rounded-lg px-4 py-2 bg-white">
                <p className="text-sm font-bold text-gray-900">4인 AI 전문가</p>
              </div>
              <div className="border-2 border-gray-300 rounded-lg px-4 py-2 bg-white">
                <p className="text-sm font-bold text-gray-900">행복한 첫 만남</p>
              </div>
            </div>
            <Link href="/chat">
              <Button
                size="lg"
                className="bg-gray-900 hover:bg-gray-800 text-white px-8 py-6 text-lg mt-4"
              >
                행복한 만남의 첫걸음
              </Button>
            </Link>
          </div>
          <div className="flex items-center justify-center h-full">
            <div className="w-full h-[500px] border-2 border-dashed border-gray-400 rounded-lg flex items-center justify-center bg-gray-100">
              <div className="text-center">
                <div className="text-6xl mb-4">🐱</div>
                <p className="text-gray-500 font-mono text-sm">CAT ILLUSTRATION</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
