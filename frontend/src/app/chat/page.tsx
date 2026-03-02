"use client";

import { useState } from "react";
import { ArrowLeft, Send } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Navigation } from "@/components/layout/Navigation";
import { GlobalDrawer } from "@/components/layout/GlobalDrawer";
import { BreedPopover } from "@/components/BreedPopover";

interface Message {
  role: "user" | "ai";
  content: string;
}

const initialMessages: Message[] = [
  {
    role: "user",
    content: "처음 고양이를 키우려고 하는데, 온순하고 사람을 잘 따르는 품종을 추천해주세요.",
  },
  {
    role: "ai",
    content: "처음 고양이를 키우시는 분께는 래그돌을 추천드립니다.",
  },
];

export default function ChatPage() {
  const router = useRouter();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-screen w-full flex flex-col bg-white">
      <Navigation onMenuClick={() => setDrawerOpen(true)} fullWidth hideNewChat />
      <GlobalDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      <div className="flex-1 flex overflow-hidden">
        {/* Column 1: Chat */}
        <div className="flex-1 flex flex-col border-r-2 border-gray-300">
          <div className="h-16 px-4 border-b-2 border-gray-300 flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-100 rounded transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h2 className="text-lg font-bold text-gray-900">새 대화</h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) =>
              msg.role === "user" ? (
                <div key={i} className="flex justify-end">
                  <div className="bg-gray-200 border-2 border-gray-300 rounded-2xl px-4 py-3 max-w-md">
                    <p className="text-gray-900 text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ) : (
                <div key={i} className="flex justify-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-gray-900 border-2 border-gray-400 flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-white text-xs font-bold">Z</span>
                  </div>
                  <div className="bg-white border-2 border-gray-300 rounded-2xl px-4 py-3 max-w-md">
                    <p className="text-gray-900 text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ),
            )}
          </div>

          <div className="border-t-2 border-gray-300 p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="메시지를 입력하세요..."
                className="flex-1 border-2 border-gray-300 focus:border-gray-900 rounded-lg px-4 py-2"
              />
              <Button
                onClick={handleSend}
                className="bg-gray-900 text-white hover:bg-gray-800 px-4"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Column 2: Results Panel */}
        <div className="w-[520px] bg-gray-50 flex flex-col">
          <div className="flex-shrink-0 p-4 border-b-2 border-gray-300">
            <h3 className="text-lg font-bold text-gray-900 mb-3">참고 출처</h3>
            <div className="space-y-3">
              {[
                { title: "래그돌 품종 특성 및 관리 가이드", source: "한국고양이협회", url: "koreacats.or.kr/breeds/ragdoll" },
                { title: "온순한 고양이 품종 TOP 10", source: "펫케어 매거진", url: "petcare.com/gentle-cat-breeds" },
                { title: "처음 고양이 입양자를 위한 품종 선택 가이드", source: "동물보호협회", url: "animalcare.org/first-time-cat-owner" },
              ].map((doc, index) => (
                <div key={index} className="bg-white border-2 border-gray-300 rounded-lg p-3 hover:border-gray-400 transition-colors">
                  <p className="text-sm font-medium text-gray-900 mb-1">{doc.title}</p>
                  <p className="text-xs text-gray-600 mb-1">{doc.source}</p>
                  <p className="text-xs text-gray-500 font-mono">{doc.url}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="flex-1 p-4 overflow-y-auto flex items-start justify-center">
            <div className="w-full max-w-[480px]">
              <div className="border-2 border-gray-300 bg-white shadow-md rounded-lg overflow-hidden">
                <div className="w-full h-[360px] bg-gray-200 border-b-2 border-gray-300 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl mb-2">🐱</div>
                    <p className="text-gray-500 font-mono text-xs">BREED IMAGE</p>
                  </div>
                </div>
                <div className="p-5 space-y-3">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">래그돌</h3>
                    <p className="text-sm text-gray-500 mt-1">Ragdoll</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {["#온순함", "#실내적응", "#애정많음", "#조용함"].map((tag, i) => (
                      <span key={i} className="border-2 border-gray-400 text-gray-700 rounded-full px-3 py-1 text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="h-[2px] bg-gray-300" />
                  <p className="text-sm text-gray-700 leading-relaxed">
                    래그돌은 매우 온순하고 사람을 잘 따르는 대형 고양이입니다. 안아주면 인형처럼 축 늘어지는 특성이 있어 래그돌이라는 이름이 붙었습니다.
                  </p>
                  <p className="text-xs text-gray-500 pt-1">출처: 한국고양이협회</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
