import { Home, BrainCircuit, CheckCircle } from "lucide-react";

const steps = [
  {
    number: 1,
    icon: Home,
    title: "집사님의 일상을 들려주세요",
    description: "함께 사는 가족, 집 안 환경, 활동량 등 집사님의 생활 패턴을 알려주세요.",
  },
  {
    number: 2,
    icon: BrainCircuit,
    title: "데이터로 최적의 솔루션을 찾아요",
    description: "Head Butler가 집사님의 마음을 읽고, AI 전문가 팀을 구성합니다.",
  },
  {
    number: 3,
    icon: CheckCircle,
    title: "전문가의 맞춤 처방이 시작됩니다",
    description: "Matchmaker / Liaison / Care Team이 집사님께 딱 맞는 답변을 드립니다.",
  },
];

export function HowItWorks() {
  return (
    <section className="w-full border-b border-gray-300 bg-gray-100">
      <div className="max-w-[1440px] mx-auto px-16 py-20">
        <h2 className="text-3xl font-bold text-center mb-16 text-gray-900">
          우리 아이를 위한 맞춤 케어, 이렇게 진행돼요
        </h2>
        <div className="grid grid-cols-3 gap-12">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <div key={step.number} className="text-center space-y-4">
                <div className="mx-auto w-24 h-24 border-2 border-gray-900 rounded-full flex items-center justify-center bg-gray-100 relative">
                  <Icon className="w-10 h-10 text-gray-700" strokeWidth={1.5} />
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {step.number}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-gray-900">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
