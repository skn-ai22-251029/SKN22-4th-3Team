import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

const features = [
  {
    emoji: "🧩",
    title: "맞춤형 품종 매칭",
    description: "주거환경·알레르기·활동량 기반. 67종 중 나에게 맞는 묘종 추천.",
  },
  {
    emoji: "🔭",
    title: "입양 & 구조 연계",
    description: "국가동물보호정보시스템 실시간 조회. 입양 절차·서류·비용 안내.",
  },
  {
    emoji: "⚖️",
    title: "합사 & 행동 상담",
    description: "다중묘 합사 가이드. 공격성·분리불안 등 행동학적 솔루션 제공.",
  },
  {
    emoji: "🩺",
    title: "생애주기 건강 케어",
    description: "증상별 초기 대응 가이드(Triage). 연령·묘종별 영양 관리 조언.",
  },
];

export function Features() {
  return (
    <section className="w-full border-b border-gray-300 bg-gray-50">
      <div className="max-w-[1440px] mx-auto px-16 py-20">
        <h2 className="text-3xl font-bold text-center mb-16 text-gray-900">ZIPSA가 도와드리는 것들</h2>
        <div className="grid grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="border-2 border-gray-300 bg-white">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-4xl">{feature.emoji}</span>
                  <CardTitle className="text-xl text-gray-900">{feature.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600 leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
