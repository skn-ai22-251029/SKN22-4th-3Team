"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { X, Plus, Search, Cat, LogIn, Trash2 } from "lucide-react";
import * as VisuallyHidden from "@radix-ui/react-visually-hidden";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
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

interface ChatSession {
  id: string;
  title: string;
  date: string;
}

const mockSessions: ChatSession[] = [
  { id: "1", title: "아파트에 맞는 고양이 추천", date: "2024.03.01" },
  { id: "2", title: "래그돌 성격 상담", date: "2024.02.28" },
  { id: "3", title: "보호소 입양 절차 문의", date: "2024.02.27" },
  { id: "4", title: "고양이 알레르기 품종", date: "2024.02.25" },
  { id: "5", title: "브리티시 숏헤어 특징", date: "2024.02.24" },
  { id: "6", title: "실내 고양이 기르기", date: "2024.02.20" },
  { id: "7", title: "코리안숏헤어 vs 러시안블루", date: "2024.02.18" },
];

interface GlobalDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function GlobalDrawer({ isOpen, onClose }: GlobalDrawerProps) {
  const { status } = useSession();
  const router = useRouter();
  const isLoggedIn = status === "authenticated";
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedSession, setSelectedSession] = useState<ChatSession | null>(null);

  const handleDelete = (session: ChatSession) => {
    setSelectedSession(session);
    setIsDeleting(true);
  };

  const confirmDelete = () => {
    setIsDeleting(false);
    onClose();
  };

  const content = isLoggedIn ? (
    <div className="h-full flex flex-col">
      <div className="flex-shrink-0 border-b-2 border-gray-300 p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-gray-900">ZIPSA</h1>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-900 transition-colors">
            <X className="w-5 h-5" strokeWidth={2} />
          </button>
        </div>
        <Button
          variant="outline"
          onClick={() => { router.push("/chat"); onClose(); }}
          className="w-full border-2 border-gray-900 bg-white text-gray-900 hover:bg-gray-100 gap-2"
        >
          <Plus className="w-4 h-4" />
          새 채팅
        </Button>
      </div>

      <div className="flex-shrink-0 border-b-2 border-gray-300">
        <button
          onClick={() => { router.push("/meme"); onClose(); }}
          className="w-full h-12 px-4 flex items-center gap-3 hover:bg-gray-100 transition-colors"
        >
          <Cat className="w-5 h-5 text-gray-600" strokeWidth={2} />
          <span className="text-sm text-gray-900 font-medium">냥심 번역기</span>
        </button>
        <button className="w-full h-12 px-4 flex items-center gap-3 hover:bg-gray-100 transition-colors">
          <Search className="w-5 h-5 text-gray-600" strokeWidth={2} />
          <span className="text-sm text-gray-900 font-medium">품종 탐색</span>
        </button>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="px-4 pt-4 pb-2">
          <p className="text-xs text-gray-500 font-medium">최근 대화</p>
        </div>
        <ScrollArea className="h-full px-2">
          <div className="space-y-1 pb-4">
            {mockSessions.map((session) => (
              <div
                key={session.id}
                onClick={() => { router.push(`/chat?session=${session.id}`); onClose(); }}
                className="w-full h-12 px-3 rounded-lg hover:bg-gray-100 transition-colors flex items-center gap-2 group relative cursor-pointer"
              >
                <div className="flex-1 text-left min-w-0">
                  <p className="text-sm text-gray-900 truncate font-medium">{session.title}</p>
                </div>
                <div className="flex items-center flex-shrink-0">
                  <span className="text-xs text-gray-400 whitespace-nowrap group-hover:opacity-0 transition-opacity">
                    {session.date}
                  </span>
                  <button
                    className="absolute right-3 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-600"
                    onClick={(e) => { e.stopPropagation(); handleDelete(session); }}
                  >
                    <Trash2 className="w-4 h-4" strokeWidth={2} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  ) : (
    <div className="h-full flex flex-col">
      <div className="flex-shrink-0 border-b-2 border-gray-300 p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-gray-900">ZIPSA</h1>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-900 transition-colors">
            <X className="w-5 h-5" strokeWidth={2} />
          </button>
        </div>
        <Button
          variant="outline"
          onClick={() => { router.push("/chat"); onClose(); }}
          className="w-full border-2 border-gray-900 bg-white text-gray-900 hover:bg-gray-100 gap-2"
        >
          <Plus className="w-4 h-4" />
          새 채팅
        </Button>
      </div>

      <div className="flex-shrink-0 border-b-2 border-gray-300">
        <button className="w-full h-12 px-4 flex items-center gap-3 hover:bg-gray-100 transition-colors">
          <Cat className="w-5 h-5 text-gray-600" strokeWidth={2} />
          <span className="text-sm text-gray-900 font-medium">냥심 번역기</span>
        </button>
        <button className="w-full h-12 px-4 flex items-center gap-3 hover:bg-gray-100 transition-colors">
          <Search className="w-5 h-5 text-gray-600" strokeWidth={2} />
          <span className="text-sm text-gray-900 font-medium">품종 탐색</span>
        </button>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <p className="text-sm text-gray-500 text-center mb-4">로그인하면 대화 기록이 저장돼요.</p>
        <Button
          variant="outline"
          onClick={() => { router.push("/login"); onClose(); }}
          className="w-full border-2 border-gray-900 bg-white text-gray-900 hover:bg-gray-100 gap-2"
        >
          <LogIn className="w-4 h-4" />
          로그인하기
        </Button>
      </div>
    </div>
  );

  return (
    <>
      <Sheet open={isOpen} onOpenChange={onClose}>
        <SheetContent side="left" className="w-[300px] p-0 border-r-2 border-gray-300 bg-white [&>button]:hidden">
          <VisuallyHidden.Root>
            <SheetTitle>Navigation Menu</SheetTitle>
            <SheetDescription>Main navigation and chat history</SheetDescription>
          </VisuallyHidden.Root>
          {content}
        </SheetContent>
      </Sheet>

      <AlertDialog open={isDeleting} onOpenChange={setIsDeleting}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>대화 삭제 확인</AlertDialogTitle>
            <AlertDialogDescription>
              정말로 &ldquo;{selectedSession?.title}&rdquo; 대화를 삭제하시겠습니까?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setIsDeleting(false)}>취소</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete}>삭제</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
