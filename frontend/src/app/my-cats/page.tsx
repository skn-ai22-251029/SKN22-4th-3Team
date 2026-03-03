"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Navigation } from "@/components/layout/Navigation";
import { GlobalDrawer } from "@/components/layout/GlobalDrawer";
import { UserCatCard } from "@/components/chat/UserCatCard";
import { getZipsaToken, getUserCats, type UserCat } from "@/lib/api";

function AddCatCard({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="border-2 border-dashed border-gray-400 rounded-lg p-6 bg-white hover:bg-gray-50 transition-colors min-h-[320px] flex items-center justify-center w-full"
    >
      <div className="text-center space-y-3">
        <div className="w-16 h-16 rounded-full border-2 border-dashed border-gray-400 flex items-center justify-center mx-auto">
          <Plus className="w-8 h-8 text-gray-400" />
        </div>
        <p className="text-sm text-gray-500 font-medium">고양이 추가하기</p>
      </div>
    </button>
  );
}

export default function MyCatsPage() {
  const router = useRouter();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [cats, setCats] = useState<UserCat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getZipsaToken();
    if (!token) { setLoading(false); return; }
    getUserCats(token)
      .then(setCats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <Navigation onMenuClick={() => setDrawerOpen(true)} />
      <GlobalDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      <div className="max-w-[960px] mx-auto px-8 py-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-gray-900">내 고양이</h2>
          <Button
            variant="outline"
            className="border-2 border-gray-900 bg-white text-gray-900 hover:bg-gray-100 gap-2"
            onClick={() => router.push("/my-cats/new")}
          >
            <Plus className="w-5 h-5" />
            고양이 등록하기
          </Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <span className="inline-flex gap-1 items-center">
              <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "300ms" }} />
            </span>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-6">
            {cats.map((cat) => (
              <UserCatCard
                key={cat.cat_id}
                cat={cat}
                onEdit={() => router.push(`/my-cats/${cat.cat_id}`)}
              />
            ))}
            <AddCatCard onClick={() => router.push("/my-cats/new")} />
          </div>
        )}
      </div>
    </div>
  );
}
