"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Navigation } from "@/components/layout/Navigation";
import { GlobalDrawer } from "@/components/layout/GlobalDrawer";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { getZipsaToken, getUserCats, updateUserCat, deleteUserCat, type UserCat } from "@/lib/api";

export default function EditCatPage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [cat, setCat] = useState<UserCat | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [form, setForm] = useState({
    name: "",
    breed_name_ko: "",
    breed_name_en: "",
    age_months: "",
    gender: "미상",
    profile_image_url: "",
  });

  useEffect(() => {
    const token = getZipsaToken();
    if (!token) return;
    getUserCats(token)
      .then((cats) => {
        const found = cats.find((c) => c.cat_id === id);
        if (found) {
          setCat(found);
          setForm({
            name: found.name,
            breed_name_ko: found.breed_name_ko,
            breed_name_en: found.breed_name_en,
            age_months: String(found.age_months),
            gender: found.gender,
            profile_image_url: found.profile_image_url ?? "",
          });
        }
      })
      .catch(() => {});
  }, [id]);

  const set = (key: keyof typeof form, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !cat) return;
    const token = getZipsaToken();
    if (!token) return;
    setSubmitting(true);
    try {
      await updateUserCat(token, cat.cat_id, {
        name: form.name.trim(),
        breed_name_ko: form.breed_name_ko.trim(),
        breed_name_en: form.breed_name_en.trim(),
        age_months: form.age_months ? parseInt(form.age_months, 10) : 0,
        gender: form.gender,
        profile_image_url: form.profile_image_url.trim() || null,
      });
      router.push("/my-cats");
    } catch {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    const token = getZipsaToken();
    if (!token || !cat) return;
    try {
      await deleteUserCat(token, cat.cat_id);
      router.push("/my-cats");
    } catch { /* ignore */ }
  };

  if (!cat) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <span className="text-gray-400 text-sm">불러오는 중...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Navigation onMenuClick={() => setDrawerOpen(true)} />
      <GlobalDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      <div className="max-w-[480px] mx-auto px-6 py-12">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-100 rounded transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h2 className="text-2xl font-bold text-gray-900">고양이 수정</h2>
          </div>
          <button
            onClick={() => setConfirmDelete(true)}
            className="p-2 hover:bg-red-50 rounded transition-colors text-gray-400 hover:text-red-600"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">이름 *</label>
            <Input
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              placeholder="예: 나비"
              className="border-2 border-gray-300 focus:border-gray-900"
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">품종 (한국어)</label>
            <Input
              value={form.breed_name_ko}
              onChange={(e) => set("breed_name_ko", e.target.value)}
              placeholder="예: 코리안숏헤어"
              className="border-2 border-gray-300 focus:border-gray-900"
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">품종 (영어)</label>
            <Input
              value={form.breed_name_en}
              onChange={(e) => set("breed_name_en", e.target.value)}
              placeholder="예: Korean Shorthair"
              className="border-2 border-gray-300 focus:border-gray-900"
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">나이 (개월)</label>
            <Input
              type="number"
              min={0}
              value={form.age_months}
              onChange={(e) => set("age_months", e.target.value)}
              placeholder="예: 14"
              className="border-2 border-gray-300 focus:border-gray-900"
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">성별</label>
            <div className="flex gap-2">
              {(["M", "F", "미상"] as const).map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => set("gender", g)}
                  className={`flex-1 py-2 border-2 rounded-lg text-sm font-medium transition-colors ${
                    form.gender === g
                      ? "border-gray-900 bg-gray-900 text-white"
                      : "border-gray-300 text-gray-700 hover:border-gray-500"
                  }`}
                >
                  {g === "M" ? "수컷" : g === "F" ? "암컷" : "미상"}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">프로필 이미지 URL (선택)</label>
            <Input
              value={form.profile_image_url}
              onChange={(e) => set("profile_image_url", e.target.value)}
              placeholder="https://..."
              className="border-2 border-gray-300 focus:border-gray-900"
            />
          </div>

          <Button
            type="submit"
            disabled={submitting || !form.name.trim()}
            className="w-full bg-gray-900 text-white hover:bg-gray-800 disabled:opacity-50 h-11"
          >
            {submitting ? "저장 중..." : "저장하기"}
          </Button>
        </form>
      </div>

      <AlertDialog open={confirmDelete} onOpenChange={setConfirmDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>고양이 삭제</AlertDialogTitle>
            <AlertDialogDescription>
              &ldquo;{cat.name}&rdquo; 정보를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>취소</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>삭제</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
