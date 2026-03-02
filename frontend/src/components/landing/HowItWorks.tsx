import { Home, BrainCircuit, CheckCircle } from "lucide-react";

const steps = [
  {
    number: 1,
    icon: Home,
    title: "집사 환경 입력",
    description: "주거형태, 활동량, 동거인 등 설문",
  },
  {
    number: 2,
    icon: BrainCircuit,
    title: "AI 수석 집사 분석",
    description: "Head Butler가 의도를 파악하고 전문가 호출",
  },
  {
    number: 3,
    icon: CheckCircle,
    title: "맞춤 전문가 응답",
    description: "Matchmaker / Liaison / Care Team이 답변",
  },
];

export function HowItWorks() {
  return (
    <section className="w-full border-b border-gray-300 bg-gray-50">
      <div className="max-w-[1440px] mx-auto px-16 py-20">
        <h2 className="text-3xl font-bold text-center mb-16 text-gray-900">어떻게 작동하나요?</h2>
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
