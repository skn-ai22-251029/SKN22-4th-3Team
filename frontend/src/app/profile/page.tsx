"use client";

import { useState, useEffect, useRef } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Cat, User, X } from "lucide-react";
import DaumPostcode from "react-daum-postcode";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Navigation } from "@/components/layout/Navigation";
import { GlobalDrawer } from "@/components/layout/GlobalDrawer";
import {
  getZipsaToken,
  getProfile,
  updateProfile,
  getAvatarPresignUrl,
} from "@/lib/api";

// ── 값 매핑 ─────────────────────────────────────────────────────────────────

const HOUSING_DISPLAY = ["아파트", "주택", "원룸"] as const;
const HOUSING_MAP: Record<string, string> = { 아파트: "apartment", 주택: "house", 원룸: "studio" };
const HOUSING_REVERSE: Record<string, string> = { apartment: "아파트", house: "주택", studio: "원룸" };

const ACTIVITY_DISPLAY = ["정적", "보통", "활동적"] as const;
const ACTIVITY_MAP: Record<string, string> = { 정적: "low", 보통: "medium", 활동적: "high" };
const ACTIVITY_REVERSE: Record<string, string> = { low: "정적", medium: "보통", high: "활동적" };

const EXPERIENCE_DISPLAY = ["초보", "경력", "베테랑"] as const;
const EXPERIENCE_MAP: Record<string, string> = { 초보: "beginner", 경력: "intermediate", 베테랑: "expert" };
const EXPERIENCE_REVERSE: Record<string, string> = { beginner: "초보", intermediate: "경력", expert: "베테랑" };

const WORK_STYLE_DISPLAY = ["거의 없음", "4시간 미만", "4~8시간", "8시간 이상"] as const;
const WORK_STYLE_MAP: Record<string, string> = {
  "거의 없음": "none",
  "4시간 미만": "under_4h",
  "4~8시간": "4_8h",
  "8시간 이상": "over_8h",
};
const WORK_STYLE_REVERSE: Record<string, string> = {
  none: "거의 없음",
  under_4h: "4시간 미만",
  "4_8h": "4~8시간",
  over_8h: "8시간 이상",
};

const GENDER_DISPLAY = ["남성", "여성", "미설정"] as const;
const GENDER_MAP: Record<string, string> = { 남성: "M", 여성: "F", 미설정: "미설정" };
const GENDER_REVERSE: Record<string, string> = { M: "남성", F: "여성", 미설정: "미설정" };

const TRAIT_OPTIONS = [
  "#조용함", "#애교많음", "#독립적", "#활발함",
  "#무릎냥이", "#호기심많음", "#낯가림없음", "#그루밍적음",
];

export default function ProfilePage() {
  const { data: session } = useSession();
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  // 기본 정보
  const [nickname, setNickname] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("미설정");
  const [contact, setContact] = useState("");
  const [roadAddress, setRoadAddress] = useState("");
  const [detailAddress, setDetailAddress] = useState("");
  const [showPostcode, setShowPostcode] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  // 양육 환경
  const [housing, setHousing] = useState("아파트");
  const [activity, setActivity] = useState("보통");
  const [experience, setExperience] = useState("초보");
  const [workStyle, setWorkStyle] = useState("거의 없음");
  const [livesAlone, setLivesAlone] = useState(true);
  const [companions, setCompanions] = useState<string[]>([]);
  const [allergy, setAllergy] = useState("없음");
  const [traits, setTraits] = useState<string[]>([]);

  // 초기 데이터 로드
  useEffect(() => {
    const token = getZipsaToken();
    if (!token) { router.push("/login"); return; }

    getProfile(token)
      .then((profile) => {
        setNickname(profile.nickname ?? "");
        setAge(profile.age != null ? String(profile.age) : "");
        setGender(GENDER_REVERSE[profile.gender ?? "미설정"] ?? "미설정");
        setContact(profile.contact ?? "");
        setRoadAddress(profile.address ?? "");
        setAvatarUrl(profile.avatar_url ?? null);

        const p = profile.preferences;
        setHousing(HOUSING_REVERSE[p.housing] ?? "아파트");
        setActivity(ACTIVITY_REVERSE[p.activity] ?? "보통");
        setExperience(EXPERIENCE_REVERSE[p.experience] ?? "초보");
        setWorkStyle(WORK_STYLE_REVERSE[p.work_style ?? ""] ?? "거의 없음");
        setAllergy(p.allergy ? "있음" : "없음");

        const hasChildren = p.has_children || p.companion.includes("어린 아이");
        const hasDog = p.has_dog || p.companion.includes("강아지");
        const hasCat = p.has_cat || p.companion.includes("고양이 있음");
        const family = p.companion.includes("가족");

        const loadedCompanions: string[] = [];
        if (hasChildren) loadedCompanions.push("어린 아이");
        if (hasDog) loadedCompanions.push("강아지");
        if (family) loadedCompanions.push("가족");
        if (hasCat) loadedCompanions.push("고양이 있음");

        setLivesAlone(loadedCompanions.length === 0);
        setCompanions(loadedCompanions);
        setTraits(p.traits ?? []);
      })
      .catch(() => {/* 프로필 없으면 빈 폼 */})
      .finally(() => setLoading(false));
  }, [router]);

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

  const handleAddressComplete = (data: { roadAddress: string }) => {
    setRoadAddress(data.roadAddress);
    setShowPostcode(false);
  };

  // 사진 변경: PAR 발급 → 파일 직접 OCI 업로드 → avatar_url 상태 업데이트
  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const token = getZipsaToken();
    if (!token) return;

    setUploading(true);
    try {
      const { upload_url, avatar_url } = await getAvatarPresignUrl(token);
      await fetch(upload_url, {
        method: "PUT",
        body: file,
        headers: { "Content-Type": file.type },
      });
      setAvatarUrl(avatar_url);
    } catch (err) {
      console.error("사진 업로드 실패:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    const token = getZipsaToken();
    if (!token) return;
    setSaving(true);
    try {
      const fullAddress = detailAddress
        ? `${roadAddress} ${detailAddress}`
        : roadAddress;

      await updateProfile(token, {
        nickname: nickname || null,
        age: age ? parseInt(age, 10) : null,
        gender: GENDER_MAP[gender] ?? null,
        contact: contact || null,
        address: fullAddress || null,
        avatar_url: avatarUrl,
        preferences: {
          housing: HOUSING_MAP[housing],
          activity: ACTIVITY_MAP[activity],
          experience: EXPERIENCE_MAP[experience],
          work_style: WORK_STYLE_MAP[workStyle],
          allergy: allergy === "있음",
          has_children: companions.includes("어린 아이"),
          has_dog: companions.includes("강아지"),
          has_cat: companions.includes("고양이 있음"),
          traits,
          companion: companions,
        },
      });
      router.push("/");
    } catch (err) {
      console.error("저장 실패:", err);
    } finally {
      setSaving(false);
    }
  };

  const displayAvatar = avatarUrl ?? session?.user?.image ?? null;

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-white">
        <p className="text-gray-500">불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Navigation onMenuClick={() => setDrawerOpen(true)} fullWidth hideNewChat />
      <GlobalDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      {/* 페이지 헤더 */}
      <div className="border-b-2 border-gray-300 py-4 px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-xl font-bold text-gray-900">내 정보</h1>
        </div>
      </div>

      <div className="max-w-[720px] mx-auto px-8 py-12 space-y-12">
        {/* Section 1: 기본 정보 */}
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">기본 정보</h2>
            <div className="w-full h-[2px] bg-gray-300" />
          </div>

          {/* 아바타 */}
          <div className="flex flex-col items-center space-y-2 py-4">
            <div className="w-20 h-20 rounded-full bg-gray-200 border-2 border-gray-300 overflow-hidden flex items-center justify-center">
              {displayAvatar ? (
                <img src={displayAvatar} alt="profile" className="w-full h-full object-cover" />
              ) : (
                <User className="w-10 h-10 text-gray-500" />
              )}
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="text-sm text-gray-600 hover:text-gray-900 underline disabled:opacity-50"
            >
              {uploading ? "업로드 중..." : "사진 변경"}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleAvatarChange}
            />
          </div>

          {/* 폼 필드 */}
          <div className="space-y-5">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">닉네임</label>
              <Input
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                className="w-full border-2 border-gray-300 focus:border-gray-400 rounded-lg px-4 py-3 text-base"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">나이</label>
              <Input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                className="w-32 border-2 border-gray-300 focus:border-gray-400 rounded-lg px-4 py-3 text-base"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">성별</label>
              <div className="flex gap-0 border-2 border-gray-900 rounded-lg overflow-hidden max-w-md">
                {GENDER_DISPLAY.map((option) => (
                  <button
                    key={option}
                    onClick={() => setGender(option)}
                    className={`flex-1 py-3 text-base font-medium transition-all ${
                      gender === option
                        ? "bg-gray-900 text-white"
                        : "bg-white text-gray-900 hover:bg-gray-50"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">연락처</label>
              <Input
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                className="w-full border-2 border-gray-300 focus:border-gray-400 rounded-lg px-4 py-3 text-base"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">주소</label>
              <div className="space-y-3">
                <div className="flex gap-2">
                  <Input
                    value={roadAddress}
                    readOnly
                    placeholder="주소를 검색해주세요"
                    className="flex-1 border-2 border-gray-300 bg-gray-50 rounded-lg px-4 py-3 text-base"
                  />
                  <Button
                    onClick={() => setShowPostcode(true)}
                    variant="outline"
                    className="border-2 border-gray-900 bg-white text-gray-900 hover:bg-gray-100 px-6 py-3 text-base whitespace-nowrap"
                  >
                    주소 검색
                  </Button>
                </div>
                <Input
                  value={detailAddress}
                  onChange={(e) => setDetailAddress(e.target.value)}
                  placeholder="상세주소를 입력하세요"
                  className="w-full border-2 border-gray-300 focus:border-gray-400 rounded-lg px-4 py-3 text-base"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: 양육 환경 */}
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">양육 환경</h2>
            <div className="w-full h-[2px] bg-gray-300" />
          </div>

          <div className="space-y-6">
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">거주 형태</label>
              <div className="flex gap-3">
                {HOUSING_DISPLAY.map((option) => (
                  <button
                    key={option}
                    onClick={() => setHousing(option)}
                    className={`border-2 rounded-full px-6 py-3 text-base font-medium transition-all ${
                      housing === option
                        ? "border-gray-900 bg-gray-100 text-gray-900"
                        : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">활동량</label>
              <div className="flex gap-3">
                {ACTIVITY_DISPLAY.map((option) => (
                  <button
                    key={option}
                    onClick={() => setActivity(option)}
                    className={`border-2 rounded-full px-6 py-3 text-base font-medium transition-all ${
                      activity === option
                        ? "border-gray-900 bg-gray-100 text-gray-900"
                        : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">고양이 경험</label>
              <div className="flex gap-3">
                {EXPERIENCE_DISPLAY.map((option) => (
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

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">집 비우는 시간</label>
              <div className="flex gap-3 flex-wrap">
                {WORK_STYLE_DISPLAY.map((option) => (
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

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">동거인</label>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">혼자 사시나요?</span>
                <div className="flex gap-0 border-2 border-gray-900 rounded-lg overflow-hidden">
                  {[true, false].map((val) => (
                    <button
                      key={String(val)}
                      onClick={() => {
                        setLivesAlone(val);
                        if (val) setCompanions([]);
                      }}
                      className={`px-8 py-2 text-base font-medium transition-all ${
                        livesAlone === val
                          ? "bg-gray-900 text-white"
                          : "bg-white text-gray-900 hover:bg-gray-50"
                      }`}
                    >
                      {val ? "예" : "아니오"}
                    </button>
                  ))}
                </div>
              </div>

              {!livesAlone && (
                <div className="pt-2 flex gap-4 flex-wrap">
                  {["어린 아이", "강아지", "가족"].map((option) => (
                    <label key={option} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={companions.includes(option)}
                        onChange={() => toggleCompanion(option)}
                        className="w-4 h-4 border-2 border-gray-400 rounded"
                      />
                      <span className="text-sm text-gray-700">{option}</span>
                    </label>
                  ))}
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={companions.includes("고양이 있음")}
                      onChange={() => toggleCompanion("고양이 있음")}
                      className="w-4 h-4 border-2 border-gray-400 rounded"
                    />
                    <span className="text-sm text-gray-700 flex items-center gap-1">
                      <Cat className="w-4 h-4" />
                      고양이 있음
                    </span>
                  </label>
                </div>
              )}
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">알레르기</label>
              <div className="flex gap-3">
                {["있음", "없음"].map((option) => (
                  <button
                    key={option}
                    onClick={() => setAllergy(option)}
                    className={`border-2 rounded-full px-6 py-3 text-base font-medium transition-all ${
                      allergy === option
                        ? "border-gray-900 bg-gray-100 text-gray-900"
                        : "border-gray-400 bg-white text-gray-700 hover:border-gray-600"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">원하는 성향</label>
              <div className="flex flex-wrap gap-2">
                {TRAIT_OPTIONS.map((trait) => (
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
          </div>
        </div>

        {/* 저장 버튼 */}
        <Button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-gray-900 text-white hover:bg-gray-800 border-0 py-4 text-base font-medium disabled:opacity-50"
        >
          {saving ? "저장 중..." : "저장하기"}
        </Button>
      </div>

      {/* 다음 우편번호 모달 */}
      {showPostcode && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg relative max-w-lg w-full mx-4">
            <div className="flex items-center justify-between p-4 border-b-2 border-gray-300">
              <h3 className="text-lg font-bold text-gray-900">주소 검색</h3>
              <button
                onClick={() => setShowPostcode(false)}
                className="text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg p-2 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4">
              <DaumPostcode onComplete={handleAddressComplete} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
