const journeys = [
  {
    tag: "준비",
    expert: "수석 집사",
    title: "집사님의 일상을 들려주세요",
    quote:
      "\"반가워요, 예비 집사님! 어떤 곳에서 누구와 함께 사시나요? 집사님의 소중한 생활 패턴을 알려주시면, 수석 집사가 가장 편안한 반려 생활을 설계해 드릴게요.\"",
    description: "주거 환경, 활동량, 동거인 및 알레르기 유무 확인",
  },
  {
    tag: "인연",
    expert: "매치메이커",
    title: "운명의 묘연을 찾아드릴게요",
    quote:
      "\"세상에 나쁜 고양이는 없지만, 집사님과 찰떡궁합인 아이는 있답니다! 67종의 세밀한 데이터를 분석해 집사님의 성향과 딱 맞는 '묘연'을 콕 집어 추천해 드린다냥!\"",
    description: "맞춤형 품종 매칭 및 성격 적합도 분석",
  },
  {
    tag: "만남",
    expert: "라이에종",
    title: "설레는 첫 만남을 함께해요",
    quote:
      "\"마음에 쏙 드는 아이를 찾으셨나요? 가족을 맞이하는 길은 복잡하지 않아야 해요. 실시간 보호 정보 조회부터 까다로운 입양 서류 안내까지, 라이에종이 곁에서 꼼꼼히 챙겨줄게요!\"",
    description: "국가동물보호정보시스템 연계, 입양 절차 및 비용 가이드",
  },
  {
    tag: "동행",
    expert: "케어팀",
    title: "365일 든든한 지원군이 될게요",
    quote:
      "\"이제 진짜 시작이에요! 합사 문제로 고민될 때나 아이 건강이 걱정될 때 언제든 불러주세요. 행동 전문가와 건강 주치의가 집사님의 든든한 백업 팀이 되어 우리 아이의 평생 행복을 지켜줄게요.\"",
    description: "다중묘 합사 가이드, 행동학적 솔루션, 생애주기별 건강 관리",
  },
];

export function Features() {
  return (
    <section className="w-full border-b border-gray-300 bg-white">
      <div className="max-w-[1440px] mx-auto px-16 py-20">
        <h2 className="text-3xl font-bold text-center mb-4 text-gray-900">
          함께라서 더 행복한 집사 일지
        </h2>
        <p className="text-center text-gray-500 mb-16">
          수석 집사부터 케어팀까지, AI 전문가 팀이 반려 생활의 모든 순간을 함께합니다.
        </p>
        <div className="grid grid-cols-2 gap-8">
          {journeys.map((item, index) => (
            <div key={index} className="border-2 border-gray-200 rounded-xl p-6 bg-gray-50 space-y-3">
              <div className="flex items-center gap-3">
                <span className="border border-gray-400 rounded-full px-3 py-0.5 text-xs font-semibold text-gray-600 bg-white">
                  {item.tag}
                </span>
                <span className="text-sm font-medium text-gray-500">{item.expert}</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900">{item.title}</h3>
              <p className="text-gray-600 text-sm leading-relaxed italic">{item.quote}</p>
              <p className="text-xs text-gray-400 pt-1">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
