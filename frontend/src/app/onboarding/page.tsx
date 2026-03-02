"use client";

import { Fragment, useState } from "react";
import { useRouter } from "next/navigation";
import { Check, Cat, Home, Building, DoorClosed } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { createProfile, updateProfile, getZipsaToken } from "@/lib/api";

const steps = [
  { number: 1, title: "나 소개" },
  { number: 2, title: "우리 집" },
  { number: 3, title: "함께 사는" },
  { number: 4, title: "고양이 취향" },
];

// 값 매핑: UI 표시값 → 백엔드 enum 값
const HOUSING_MAP: Record<string, string> = {
  아파트: "apartment",
  주택: "house",
  원룸: "studio",
};

const WORK_STYLE_MAP: Record<string, string> = {
  "거의 없음": "never",
  "4시간 미만": "lt4h",
  "4~8시간": "4to8h",
  "8시간 이상": "gt8h",
};

const ACTIVITY_MAP: Record<string, string> = {
  조용하게: "low",
  적당히: "medium",
  활발하게: "high",
};

const EXPERIENCE_MAP: Record<string, string> = {
  처음이에요: "beginner",
  "한두 번 있어요": "some",
  "경험 많아요": "experienced",
};

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [nickname, setNickname] = useState("");
  const [housing, setHousing] = useState("아파트");
  const [workStyle, setWorkStyle] = useState("4~8시간");
  const [livesAlone, setLivesAlone] = useState(false);
  const [companions, setCompanions] = useState<string[]>([]);
  const [allergy, setAllergy] = useState(false);
  const [activity, setActivity] = useState("적당히");
  const [experience, setExperience] = useState("처음이에요");
  const [traits, setTraits] = useState<string[]>([]);

  const toggleCompanion = (value: string) => {
    setCompanions((prev) =>
      prev.includes(value) ? prev.filter((c) => c !== value) : [...prev, value],
    );
  };

  const toggleTrait = (value: string) => {
    setTraits((prev) =>
      prev.includes(value) ? prev.filter((t) => t !== value) : [...prev, value],
    );
  };

  const handleSubmit = async () => {
    const token = getZipsaToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    setSubmitting(true);
    setError(null);

    const profileData = {
      nickname: nickname || null,
      preferences: {
        housing: HOUSING_MAP[housing] ?? "apartment",
        activity: ACTIVITY_MAP[activity] ?? "medium",
        experience: EXPERIENCE_MAP[experience] ?? "beginner",
        work_style: WORK_STYLE_MAP[workStyle] ?? null,
        allergy,
        has_children: companions.includes("어린 아이"),
        has_dog: companions.includes("강아지"),
        has_cat: companions.includes("고양이 있음"),
        traits,
        companion: livesAlone ? [] : companions,
      },
    };

    try {
      try {
        await createProfile(token, profileData);
      } catch (err) {
        // 이미 프로필이 있으면 (409) PUT으로 업데이트
        if ((err as { status?: number }).status === 409) {
          await updateProfile(token, profileData);
        } else {
          throw err;
        }
      }
      router.replace("/");
    } catch {
      setError("프로필 저장에 실패했습니다. 다시 시도해주세요.");
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Progress Stepper */}
      <div className="w-full border-b-2 border-gray-300 bg-gray-50 py-8">
        <div className="max-w-[900px] mx-auto px-8">
          <div className="flex items-start">
            {steps.map((step, index) => (
              <Fragment key={step.number}>
                <div className="flex flex-col items-center flex-shrink-0">
                  <div
                    className={`w-12 h-12 rounded-full border-2 flex items-center justify-center font-bold ${
                      step.number < currentStep
                        ? "bg-gray-900 border-gray-900"
                        : step.number === currentStep
                          ? "bg-white border-gray-900 text-gray-900"
                          : "bg-white border-gray-400 text-gray-400"
                    }`}
                  >
                    {step.number < currentStep ? (
                      <Check className="w-6 h-6 text-white" strokeWidth={3} />
                    ) : (
                      <span className="text-sm">{step.number}</span>
                    )}
                  </div>
                  <span
                    className={`text-xs mt-2 ${
                      step.number === currentStep ? "text-gray-900 font-medium" : "text-gray-500"
                    }`}
                  >
                    {step.title}
                  </span>
                </div>

                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-[2px] mx-2 mt-6 ${
                      step.number < currentStep ? "bg-gray-900" : "bg-gray-300"
                    }`}
                  />
                )}
              </Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 py-12">
        {/* Step 1: 나 소개 */}
        {currentStep === 1 && (
          <div className="max-w-[480px] w-full text-center space-y-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-3">안녕하세요, 집사님!</h1>
              <p className="text-gray-500 text-base">어떻게 불러드릴까요?</p>
            </div>
            <div className="space-y-2">
              <Input
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="닉네임을 입력해주세요"
                className="w-full border-2 border-gray-300 focus:border-gray-900 rounded-lg px-4 py-4 text-base"
              />
              <p className="text-xs text-gray-500 text-left">나중에 언제든지 변경할 수 있어요.</p>
            </div>
          </div>
        )}

        {/* Step 2: 우리 집 */}
        {currentStep === 2 && (
          <div className="max-w-[600px] w-full space-y-8">
            <div className="space-y-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  어떤 공간에서 생활하시나요?
                </h2>
                <p className="text-gray-500 text-sm">
                  고양이의 활동량과 소음 기준을 맞추는 데 활용해요.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: "아파트", icon: Building },
                  { value: "주택", icon: Home },
                  { value: "원룸", icon: DoorClosed },
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setHousing(option.value)}
                    className={`border-2 rounded-lg p-6 text-center transition-all ${
                      housing === option.value
                        ? "border-gray-900 bg-gray-100"
                        : "border-gray-300 bg-white hover:border-gray-400"
                    }`}
                  >
                    <option.icon
                      className="w-10 h-10 mx-auto mb-3 text-gray-600"
                      strokeWidth={1.5}
                    />
                    <div className="font-medium text-gray-900 text-base">{option.value}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  하루에 집을 비우는 시간은요?
                </h2>
                <p className="text-gray-500 text-sm">혼자 있어도 괜찮은 품종을 찾는 데 활용해요.</p>
              </div>
              <div className="flex gap-3 flex-wrap">
                {["거의 없음", "4시간 미만", "4~8시간", "8시간 이상"].map((option) => (
                  <button
                    key={option}
                    onClick={() => setWorkStyle(option)}
                    className={`border-2 rounded-full px-6 py-3 text-base font-medium transition-all ${
                      workStyle === option
                        ? "border-gray-900 bg-gray-100 text-gray-900"
                        : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: 함께 사는 */}
        {currentStep === 3 && (
          <div className="max-w-[600px] w-full space-y-8">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">혼자 사시나요?</h2>
              <div className="flex gap-0 border-2 border-gray-900 rounded-lg overflow-hidden">
                <button
                  onClick={() => setLivesAlone(true)}
                  className={`flex-1 py-4 text-lg font-medium transition-all ${
                    livesAlone ? "bg-gray-900 text-white" : "bg-white text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  예
                </button>
                <div className="w-[2px] bg-gray-900" />
                <button
                  onClick={() => setLivesAlone(false)}
                  className={`flex-1 py-4 text-lg font-medium transition-all ${
                    !livesAlone
                      ? "bg-gray-900 text-white"
                      : "bg-white text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  아니오
                </button>
              </div>

              {!livesAlone && (
                <div className="space-y-4 pt-4">
                  <p className="text-gray-600 text-sm">함께 사는 분을 모두 선택해주세요.</p>
                  <div className="flex flex-col gap-3">
                    <div className="flex gap-3">
                      {["어린 아이", "강아지", "가족"].map((option) => (
                        <button
                          key={option}
                          onClick={() => toggleCompanion(option)}
                          className={`border-2 rounded-full px-6 py-3 text-base font-medium transition-all ${
                            companions.includes(option)
                              ? "border-gray-900 bg-gray-100 text-gray-900"
                              : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                          }`}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={() => toggleCompanion("고양이 있음")}
                        className={`border-2 rounded-full px-6 py-3 text-base font-medium transition-all flex items-center gap-2 ${
                          companions.includes("고양이 있음")
                            ? "border-gray-900 bg-gray-100 text-gray-900"
                            : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                        }`}
                      >
                        <Cat className="w-5 h-5" />
                        고양이 있음
                      </button>
                    </div>
                  </div>
                  <p className="text-gray-500 text-xs">
                    고양이가 있으면 사이좋게 지낼 품종을 추천해드려요.
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  고양이 털 알레르기가 있으신가요?
                </h2>
                <p className="text-gray-500 text-sm">
                  알레르기가 있으면 저알레르기 품종만 추천해드려요.
                </p>
              </div>
              <div className="flex gap-0 border-2 border-gray-900 rounded-lg overflow-hidden">
                <button
                  onClick={() => setAllergy(true)}
                  className={`flex-1 py-4 text-lg font-medium transition-all ${
                    allergy ? "bg-gray-900 text-white" : "bg-white text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  예
                </button>
                <div className="w-[2px] bg-gray-900" />
                <button
                  onClick={() => setAllergy(false)}
                  className={`flex-1 py-4 text-lg font-medium transition-all ${
                    !allergy ? "bg-gray-900 text-white" : "bg-white text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  아니오
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: 고양이 취향 */}
        {currentStep === 4 && (
          <div className="max-w-[600px] w-full space-y-8">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-900">평소 생활 패턴이 어떠세요?</h2>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: "조용하게", subtitle: "독서, 영화" },
                  { value: "적당히", subtitle: "산책, 취미" },
                  { value: "활발하게", subtitle: "운동, 아웃도어" },
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setActivity(option.value)}
                    className={`border-2 rounded-lg p-6 text-center transition-all ${
                      activity === option.value
                        ? "border-gray-900 bg-gray-100"
                        : "border-gray-300 bg-white hover:border-gray-400"
                    }`}
                  >
                    <div className="font-bold text-gray-900 text-base mb-1">{option.value}</div>
                    <div className="text-gray-500 text-sm">{option.subtitle}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-900">
                고양이를 키워본 경험이 있으신가요?
              </h2>
              <div className="flex gap-3">
                {["처음이에요", "한두 번 있어요", "경험 많아요"].map((option) => (
                  <button
                    key={option}
                    onClick={() => setExperience(option)}
                    className={`border-2 rounded-full px-6 py-3 text-base font-medium transition-all ${
                      experience === option
                        ? "border-gray-900 bg-gray-100 text-gray-900"
                        : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  원하는 고양이 성향을 골라주세요. (복수 선택)
                </h2>
                <p className="text-gray-500 text-sm">선택하지 않아도 괜찮아요.</p>
              </div>
              <div className="flex flex-wrap gap-3">
                {[
                  "#조용함",
                  "#애교많음",
                  "#독립적",
                  "#활발함",
                  "#무릎냥이",
                  "#호기심많음",
                  "#낯가림없음",
                  "#그루밍적음",
                ].map((trait) => (
                  <button
                    key={trait}
                    onClick={() => toggleTrait(trait)}
                    className={`border-2 rounded-full px-5 py-2 text-sm font-medium transition-all ${
                      traits.includes(trait)
                        ? "border-gray-900 bg-gray-100 text-gray-900"
                        : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                    }`}
                  >
                    {trait}
                  </button>
                ))}
              </div>
            </div>

            {error && <p className="text-red-500 text-sm">{error}</p>}
          </div>
        )}
      </div>

      {/* Bottom Navigation */}
      <div className="border-t-2 border-gray-300 bg-white py-6">
        <div className="max-w-[900px] mx-auto px-8 flex items-center justify-between">
          {currentStep > 1 ? (
            <Button
              onClick={() => setCurrentStep(currentStep - 1)}
              className="text-gray-600 hover:text-gray-900 bg-transparent hover:bg-transparent text-base px-4 py-2"
            >
              이전
            </Button>
          ) : (
            <div />
          )}
          <Button
            onClick={() => {
              if (currentStep < 4) {
                setCurrentStep(currentStep + 1);
              } else {
                handleSubmit();
              }
            }}
            disabled={submitting}
            className="bg-gray-900 text-white hover:bg-gray-800 px-8 py-2 text-base disabled:opacity-50"
          >
            {submitting ? "저장 중..." : currentStep === 4 ? "시작하기" : "다음"}
          </Button>
        </div>
      </div>
    </div>
  );
}
