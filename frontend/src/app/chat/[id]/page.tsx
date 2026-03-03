"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Navigation } from "@/components/layout/Navigation";
import { GlobalDrawer } from "@/components/layout/GlobalDrawer";
import ReactMarkdown from "react-markdown";
import { BreedPopover } from "@/components/BreedPopover";
import { CatCard } from "@/components/chat/CatCard";
import { RescueCatCard } from "@/components/chat/RescueCatCard";
import {
  getZipsaToken,
  createSession,
  getMessages,
  streamChat,
  type ChatMessage,
  type Recommendation,
  type RagDoc,
  type RescueCat,
} from "@/lib/api";
import { useZipsaStore } from "@/store/zipsa";

// ── AI 메시지 마크다운 렌더링 + 품종명 BreedPopover 인라인 주입 ──────────────

function MarkdownMessage({
  content,
  recommendations,
  onViewDetails,
}: {
  content: string;
  recommendations: Recommendation[];
  onViewDetails: (nameKo: string) => void;
}) {
  const injectPopovers = (text: string): React.ReactNode => {
    if (!recommendations.length) return text;
    const names = recommendations.map((r) => r.name_ko).filter(Boolean);
    if (!names.length) return text;
    const escaped = names.map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const pattern = new RegExp(`(${escaped.join("|")})`, "g");
    const parts = text.split(pattern);
    return parts.map((part, i) => {
      const rec = recommendations.find((r) => r.name_ko === part);
      if (rec) {
        return (
          <BreedPopover
            key={i}
            triggerText={part}
            breedKorean={rec.name_ko}
            breedEnglish={rec.name_en}
            tags={rec.tags}
            summary={rec.summary}
            onViewDetails={() => onViewDetails(rec.name_ko)}
          />
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <ReactMarkdown
      components={{
        p: ({ children }) => (
          <p className="mb-2 last:mb-0">
            {React.Children.map(children, (child) =>
              typeof child === "string" ? injectPopovers(child) : child
            )}
          </p>
        ),
        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
        ul: ({ children }) => <ul className="list-disc pl-4 space-y-1 my-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-4 space-y-1 my-1">{children}</ol>,
        li: ({ children }) => <li>{children}</li>,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline break-all text-xs">
            {children}
          </a>
        ),
        hr: () => <hr className="my-2 border-gray-200" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// ── 컴포넌트 ─────────────────────────────────────────────────────────────────

export default function ChatSessionPage() {
  const router = useRouter();
  const params = useParams();
  const paramId = params.id as string;
  const isNew = paramId === "new";
  const resolvedIdRef = useRef<string | null>(isNew ? null : paramId);
  const profile = useZipsaStore((s) => s.profile);
  const addSession = useZipsaStore((s) => s.addSession);
  const updateSession = useZipsaStore((s) => s.updateSession);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState("");
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [ragDocs, setRagDocs] = useState<RagDoc[]>([]);
  const [rescueCats, setRescueCats] = useState<RescueCat[]>([]);
  const [selectedBreed, setSelectedBreed] = useState(0);
  const [selectedRescue, setSelectedRescue] = useState(0);
  // 0 = breed panel, 1 = rescue panel
  const [panelMode, setPanelMode] = useState<"breed" | "rescue">("breed");
  const [sessionTitle, setSessionTitle] = useState("새 대화");
  const [creating, setCreating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sendingRef = useRef(false);          // handleSend 중복 실행 방지
  const loadedSessionRef = useRef<string | null>(null); // getMessages 중복 호출 방지

  // 메시지 로드 (기존 세션만, 세션당 1회)
  useEffect(() => {
    if (isNew) return;
    if (loadedSessionRef.current === paramId) return;
    loadedSessionRef.current = paramId;
    const token = getZipsaToken();
    if (!token) return;
    getMessages(token, paramId)
      .then((msgs) => {
        setMessages(msgs);
        const lastAI = [...msgs].reverse().find((m) => m.role === "ai");
        if (lastAI) {
          if (lastAI.recommendations?.length) {
            setRecommendations(lastAI.recommendations);
            setPanelMode("breed");
          }
          if (lastAI.rag_docs?.length) setRagDocs(lastAI.rag_docs);
          if (lastAI.rescue_cats?.length) {
            setRescueCats(lastAI.rescue_cats);
            setPanelMode("rescue");
          }
        }
        const firstHuman = msgs.find((m) => m.role === "human");
        if (firstHuman) setSessionTitle(firstHuman.content.slice(0, 30));
      })
      .catch(() => {});
  }, [paramId, isNew]);

  // 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamContent]);

  const handleViewDetails = useCallback((nameKo: string) => {
    const idx = recommendations.findIndex((r) => r.name_ko === nameKo);
    if (idx >= 0) setSelectedBreed(idx);
  }, [recommendations]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || streaming || sendingRef.current) return;
    sendingRef.current = true;
    const token = getZipsaToken();
    if (!token) { sendingRef.current = false; return; }

    // 새 채팅이면 첫 메시지 전송 시 세션 생성
    if (!resolvedIdRef.current) {
      setCreating(true);
      try {
        const session = await createSession(token);
        resolvedIdRef.current = session.session_id;
        addSession(session);
      } catch {
        setCreating(false);
        sendingRef.current = false;
        return;
      }
      setCreating(false);
    }
    const activeSessionId = resolvedIdRef.current;

    setInput("");
    const userMsg: ChatMessage = {
      message_id: crypto.randomUUID(),
      session_id: activeSessionId,
      role: "human",
      content: text,
      recommendations: [],
      rag_docs: [],
      rescue_cats: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setStreaming(true);
    setStreamContent("");

    let fullContent = "";
    let newRecs: Recommendation[] = [];
    let newDocs: RagDoc[] = [];
    let newRescueCats: RescueCat[] = [];

    try {
      for await (const event of streamChat(token, activeSessionId, text, profile)) {
        if (event.type === "token" && typeof event.content === "string") {
          fullContent += event.content;
          setStreamContent(fullContent);
        } else if (event.type === "recommendations" && Array.isArray(event.data)) {
          newRecs = event.data as Recommendation[];
          setRecommendations(newRecs);
          setSelectedBreed(0);
          setPanelMode("breed");
        } else if (event.type === "rag_docs" && Array.isArray(event.data)) {
          newDocs = event.data as RagDoc[];
          setRagDocs(newDocs);
        } else if (event.type === "rescue_cats" && Array.isArray(event.data)) {
          newRescueCats = event.data as RescueCat[];
          setRescueCats(newRescueCats);
          setSelectedRescue(0);
          setPanelMode("rescue");
        }
      }
    } catch (err) {
      console.error("스트리밍 오류:", err);
    } finally {
      const aiMsg: ChatMessage = {
        message_id: crypto.randomUUID(),
        session_id: activeSessionId,
        role: "ai",
        content: fullContent,
        recommendations: newRecs,
        rag_docs: newDocs,
        rescue_cats: newRescueCats,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setStreamContent("");
      setStreaming(false);
      sendingRef.current = false;
      if (messages.length === 0) setSessionTitle(text.slice(0, 30));
      // store 세션 업데이트 (제목 + message_count)
      updateSession(activeSessionId, { title: text.slice(0, 30), message_count: 1 });
      // 새 채팅이었으면 스트리밍 완료 후 URL 확정
      if (isNew) router.replace(`/chat/${activeSessionId}`);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div className="h-screen w-full flex flex-col bg-white">
      <Navigation onMenuClick={() => setDrawerOpen(true)} fullWidth hideNewChat />
      <GlobalDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      <div className="flex-1 flex overflow-hidden">
        {/* 채팅 영역 */}
        <div className="flex-1 flex flex-col border-r-2 border-gray-300">
          <div className="h-16 px-4 border-b-2 border-gray-300 flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-100 rounded transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h2 className="text-lg font-bold text-gray-900 truncate">{sessionTitle}</h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) =>
              msg.role === "human" ? (
                <div key={msg.message_id} className="flex justify-end">
                  <div className="bg-gray-200 border-2 border-gray-300 rounded-2xl px-4 py-3 max-w-md">
                    <p className="text-gray-900 text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ) : (
                <div key={msg.message_id} className="flex justify-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-gray-900 border-2 border-gray-400 flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-white text-xs font-bold">Z</span>
                  </div>
                  <div className="bg-white border-2 border-gray-300 rounded-2xl px-4 py-3 max-w-md text-gray-900 text-sm leading-relaxed">
                    <MarkdownMessage
                      content={msg.content}
                      recommendations={msg.recommendations ?? []}
                      onViewDetails={handleViewDetails}
                    />
                  </div>
                </div>
              ),
            )}

            {/* 세션 생성 중 로딩 */}
            {creating && (
              <div className="flex justify-center">
                <div className="bg-white border-2 border-gray-200 rounded-2xl px-4 py-3">
                  <span className="inline-flex gap-1 items-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </span>
                </div>
              </div>
            )}

            {/* 스트리밍 중인 AI 메시지 */}
            {streaming && (
              <div className="flex justify-start gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-900 border-2 border-gray-400 flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-white text-xs font-bold">Z</span>
                </div>
                <div className="bg-white border-2 border-gray-300 rounded-2xl px-4 py-3 max-w-md text-gray-900 text-sm leading-relaxed">
                  {streamContent ? (
                    <MarkdownMessage
                      content={streamContent}
                      recommendations={[]}
                      onViewDetails={handleViewDetails}
                    />
                  ) : (
                    <span className="inline-flex gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                    </span>
                  )}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t-2 border-gray-300 p-4">
            <div className="flex gap-2 items-stretch">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="메시지를 입력하세요..."
                disabled={streaming || creating}
                className="flex-1 h-10 border-2 border-gray-300 focus:border-gray-900 rounded-lg px-4"
              />
              <Button
                onClick={handleSend}
                disabled={streaming || creating || !input.trim()}
                className="h-10 bg-gray-900 text-white hover:bg-gray-800 px-4 disabled:opacity-50"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* 우측 패널 */}
        <div className="w-[520px] bg-gray-50 flex flex-col">
          {/* RAG 출처 */}
          {ragDocs.length > 0 && (
            <div className="flex-shrink-0 p-4 border-b-2 border-gray-300">
              <h3 className="text-lg font-bold text-gray-900 mb-3">참고 출처</h3>
              <div className="space-y-3">
                {ragDocs.map((doc, i) => (
                  <div key={i} className="bg-white border-2 border-gray-300 rounded-lg p-3 hover:border-gray-400 transition-colors">
                    <p className="text-sm font-medium text-gray-900 mb-1">{doc.title}</p>
                    <p className="text-xs text-gray-600 mb-1">{doc.source}</p>
                    {doc.url && <p className="text-xs text-gray-500 font-mono">{doc.url}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 패널 모드 전환 탭 (둘 다 있을 때만) */}
          {recommendations.length > 0 && rescueCats.length > 0 && (
            <div className="flex-shrink-0 border-b-2 border-gray-300 bg-white">
              <div className="flex">
                <button
                  onClick={() => setPanelMode("breed")}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                    panelMode === "breed"
                      ? "text-gray-900 border-gray-900"
                      : "text-gray-500 border-transparent hover:text-gray-700"
                  }`}
                >
                  추천 품종
                </button>
                <button
                  onClick={() => setPanelMode("rescue")}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                    panelMode === "rescue"
                      ? "text-gray-900 border-gray-900"
                      : "text-gray-500 border-transparent hover:text-gray-700"
                  }`}
                >
                  구조묘 ({rescueCats.length})
                </button>
              </div>
            </div>
          )}

          {/* 품종 탭 + CatCard */}
          {panelMode === "breed" && recommendations.length > 0 ? (
            <>
              <div className="flex-shrink-0 border-b-2 border-gray-300 bg-white">
                <div className="flex">
                  {recommendations.map((breed, i) => (
                    <button
                      key={i}
                      onClick={() => setSelectedBreed(i)}
                      className={`flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                        selectedBreed === i
                          ? "text-gray-900 border-gray-900"
                          : "text-gray-500 border-transparent hover:text-gray-700"
                      }`}
                    >
                      {breed.name_ko}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                <CatCard breed={recommendations[selectedBreed]} />
              </div>
            </>
          ) : panelMode === "rescue" && rescueCats.length > 0 ? (
            <>
              <div className="flex-shrink-0 border-b-2 border-gray-300 bg-white">
                <div className="flex overflow-x-auto">
                  {rescueCats.map((cat, i) => (
                    <button
                      key={i}
                      onClick={() => setSelectedRescue(i)}
                      className={`flex-shrink-0 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                        selectedRescue === i
                          ? "text-gray-900 border-gray-900"
                          : "text-gray-500 border-transparent hover:text-gray-700"
                      }`}
                    >
                      {cat.breed || `#${i + 1}`}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                <RescueCatCard cat={rescueCats[selectedRescue]} />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-gray-400 text-sm">품종을 추천받으면 여기에 표시됩니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
