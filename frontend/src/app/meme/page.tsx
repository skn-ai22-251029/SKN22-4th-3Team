"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Navigation } from "@/components/layout/Navigation";
import { GlobalDrawer } from "@/components/layout/GlobalDrawer";
import { getZipsaToken, analyzeMeme, createUserCat, MemeAnalyzeResponse } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";


export default function MemePage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MemeAnalyzeResponse | null>(null);

  // 내 고양이 등록 다이얼로그
  const [dialogOpen, setDialogOpen] = useState(false);
  const [catName, setCatName] = useState("");
  const [registering, setRegistering] = useState(false);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) handleFileSelect(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    const token = getZipsaToken();
    if (!token) return;
    setLoading(true);
    try {
      const res = await analyzeMeme(token, selectedFile, context);
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterCat = async () => {
    if (!catName.trim() || !result) return;
    const token = getZipsaToken();
    if (!token) return;
    setRegistering(true);
    try {
      await createUserCat(token, {
        name: catName.trim(),
        breed_name_ko: result.breed_guess,
        age_months: result.age_months,
        profile_image_url: `${API_BASE}${result.image_url}`,
        meme_text: result.meme_text,
      });
      router.push("/my-cats");
    } finally {
      setRegistering(false);
      setDialogOpen(false);
    }
  };

  const openRegisterDialog = () => {
    setCatName("");
    setDialogOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navigation onMenuClick={() => setDrawerOpen(true)} />
      <GlobalDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      <div className="flex-1 flex flex-col items-center justify-center py-12">
        <div className="w-full max-w-[1200px] px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-3">냥심 번역기</h1>
            <p className="text-gray-500 text-base">
              고양이 사진을 올리면 AI가 고양이의 속마음을 대신 전해드립니다
            </p>
          </div>
          <div className="grid grid-cols-2 gap-16">
            {/* Left Column — 업로드 */}
            <div className="flex flex-col items-center justify-center">
              {/* 업로드 박스 */}
              <div
                className={`w-[420px] h-[420px] border-4 border-dashed rounded-lg flex flex-col items-center justify-center cursor-pointer transition-colors overflow-hidden ${
                  dragging
                    ? "border-gray-700 bg-gray-100"
                    : "border-gray-400 bg-white hover:border-gray-500 hover:bg-gray-50"
                }`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
              >
                {previewUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={previewUrl}
                    alt="선택된 고양이 사진"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-gray-400 mb-4" strokeWidth={2} />
                    <p className="text-gray-600 text-center px-8 leading-relaxed">
                      고양이 사진을 드래그하거나<br />클릭해서 올려주세요
                    </p>
                  </>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelect(file);
                }}
              />

              {/* 컨텍스트 입력 */}
              <div className="w-[420px] mt-6 relative">
                <Input
                  placeholder="한 마디 덧붙여 주세요 (선택사항, 예: 오늘 밥을 거부했어요)"
                  className="w-full border-2 border-gray-300 focus:border-gray-400 rounded-lg px-4 py-3 pr-16"
                  maxLength={100}
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500">
                  {context.length}/100
                </span>
              </div>

              {/* 분석 버튼 */}
              <Button
                className="w-[420px] mt-4 bg-gray-900 text-white hover:bg-gray-800 border-0 rounded-lg py-6 text-base font-medium disabled:opacity-50"
                disabled={!selectedFile || loading}
                onClick={handleAnalyze}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    분석 중...
                  </span>
                ) : (
                  "분석 시작"
                )}
              </Button>
            </div>

            {/* Right Column — 결과 */}
            <div className="flex flex-col items-center justify-center">
              {/* 폴라로이드 카드 */}
              <div
                className="bg-white p-6 shadow-lg"
                style={{ transform: "rotate(2deg)", borderRadius: "4px" }}
              >
                <div className="w-[320px] h-[320px] bg-gray-200 border-2 border-gray-300 flex items-center justify-center overflow-hidden">
                  {result ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={`${API_BASE}${result.image_url}`}
                      alt="분석된 고양이"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-center">
                      <div className="text-6xl mb-2">🐱</div>
                      <p className="text-gray-500 font-mono text-xs">CAT PHOTO</p>
                    </div>
                  )}
                </div>

                <div className="mt-4 px-2">
                  {result ? (
                    <>
                      <p className="text-gray-800 italic text-center leading-relaxed text-sm">
                        {result.meme_text}
                      </p>
                      <div className="flex justify-center gap-2 mt-3">
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                          {result.breed_guess}
                        </span>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                          {result.age_guess}
                        </span>
                      </div>
                    </>
                  ) : (
                    <p className="text-gray-800 italic text-center leading-relaxed text-sm">
                      "인간아, 지금 당장 간식을<br />내놓지 않으면 후회할 거다냥"
                    </p>
                  )}
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex gap-3 mt-8">
                <Button
                  className="bg-gray-900 text-white hover:bg-gray-800 border-0 px-6 py-2 disabled:opacity-50"
                  disabled={!result}
                  onClick={openRegisterDialog}
                >
                  내 고양이로 등록
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 내 고양이 등록 다이얼로그 */}
      <AlertDialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>내 고양이로 등록</AlertDialogTitle>
          </AlertDialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">이름 *</label>
              <Input
                placeholder="예: 나비"
                value={catName}
                onChange={(e) => setCatName(e.target.value)}
                className="border-2 border-gray-300 focus:border-gray-900"
                autoFocus
              />
            </div>
            {result && (
              <div className="text-sm text-gray-500 space-y-1">
                <p>품종: {result.breed_guess || "—"}</p>
                <p>나이: {result.age_months ? `약 ${result.age_months}개월` : "—"}</p>
              </div>
            )}
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={registering}>취소</AlertDialogCancel>
            <AlertDialogAction
              disabled={!catName.trim() || registering}
              onClick={(e) => {
                e.preventDefault();
                handleRegisterCat();
              }}
              className="bg-gray-900 text-white hover:bg-gray-800"
            >
              {registering ? "등록 중..." : "등록하기"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
