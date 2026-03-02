import { Button } from "@/components/ui/button";
import Link from "next/link";

export function FinalCTA() {
  return (
    <section className="w-full bg-gray-900">
      <div className="max-w-[1440px] mx-auto px-16 py-24">
        <div className="text-center space-y-6">
          <h2 className="text-4xl font-bold text-white leading-tight">
            서로에게 맞는 만남이<br />평생 함께할 수 있습니다.
          </h2>
          <p className="text-gray-300 text-lg">
            ZIPSA가 당신과 고양이, 모두를 위한 최선의 매칭을 찾아드릴게요.
          </p>
          <Link href="/chat">
            <Button
              size="lg"
              className="bg-white hover:bg-gray-100 text-gray-900 px-12 py-6 text-lg mt-4"
            >
              지금 시작하기
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
