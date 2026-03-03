"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { ChevronDown, User, LogOut, Cat, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useZipsaStore } from "@/store/zipsa";

interface NavigationProps {
  onMenuClick?: () => void;
  fullWidth?: boolean;
  hideNewChat?: boolean;
}

export function Navigation({ onMenuClick, fullWidth = false, hideNewChat = false }: NavigationProps) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const isLoggedIn = status === "authenticated";
  const profile = useZipsaStore((s) => s.profile);
  const resetStore = useZipsaStore((s) => s.reset);

  // OAuth 기본값
  const rawName = session?.user?.name;
  const oauthNickname =
    rawName && rawName !== "undefined" && rawName !== "null" ? rawName : "집사님";
  const oauthAvatar = session?.user?.image ?? null;

  // 뱃지: 프로필 설정값 우선, 없으면 OAuth
  const badgeAvatar = profile?.avatar_url ?? oauthAvatar;
  const badgeNickname = profile?.nickname ?? oauthNickname;

  return (
    <nav className="w-full h-16 border-b-2 border-gray-300 bg-white">
      <div className={`h-full flex items-center justify-between ${fullWidth ? "px-6" : "max-w-[1440px] mx-auto px-16"}`}>
        {/* Left: Hamburger + Logo */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="text-gray-900 hover:bg-gray-100 p-2 rounded-lg transition-colors"
          >
            <Menu className="w-6 h-6" strokeWidth={2} />
          </button>
          <button onClick={() => router.push("/")} className="text-2xl font-bold text-gray-900 tracking-tight">
            ZIPSA
          </button>
        </div>

        {/* Right */}
        <div className="flex items-center gap-4">
          {isLoggedIn ? (
            <>
              {!hideNewChat && (
                <Button
                  onClick={() => router.push("/chat/new")}
                  className="bg-gray-900 hover:bg-gray-800 text-white rounded-full px-6"
                >
                  새 채팅
                </Button>
              )}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                    {badgeAvatar ? (
                      <img src={badgeAvatar} alt="profile" className="w-8 h-8 rounded-full border-2 border-gray-400 object-cover" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gray-300 border-2 border-gray-400 flex items-center justify-center">
                        <User className="w-4 h-4 text-gray-600" strokeWidth={2} />
                      </div>
                    )}
                    <span className="text-gray-900 font-medium">{badgeNickname}</span>
                    <ChevronDown className="w-4 h-4 text-gray-600" strokeWidth={2} />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-[200px] border-2 border-gray-300 bg-white shadow-lg p-0">
                  <div className="flex items-center gap-3 px-4 h-[44px] border-b-2 border-gray-300">
                    {oauthAvatar ? (
                      <img src={oauthAvatar} alt="profile" className="w-8 h-8 rounded-full border-2 border-gray-400 object-cover flex-shrink-0" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gray-300 border-2 border-gray-400 flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4 text-gray-600" strokeWidth={2} />
                      </div>
                    )}
                    <div className="flex flex-col overflow-hidden">
                      <span className="text-sm font-medium text-gray-900 truncate">{oauthNickname}</span>
                      <span className="text-xs text-gray-500 truncate">{session?.user?.email}</span>
                    </div>
                  </div>
                  <DropdownMenuItem
                    onClick={() => router.push("/profile")}
                    className="cursor-pointer h-[44px] px-4 flex items-center gap-3 hover:bg-gray-100"
                  >
                    <User className="w-5 h-5 text-gray-600" strokeWidth={1.5} />
                    <span className="text-gray-900">내 프로필</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => router.push("/my-cats")}
                    className="cursor-pointer h-[44px] px-4 flex items-center gap-3 hover:bg-gray-100"
                  >
                    <Cat className="w-5 h-5 text-gray-600" strokeWidth={1.5} />
                    <span className="text-gray-900">내 고양이</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-gray-300 h-[2px] my-0" />
                  <DropdownMenuItem
                    onClick={() => { resetStore(); signOut({ callbackUrl: "/" }); }}
                    className="cursor-pointer h-[44px] px-4 flex items-center gap-3 hover:bg-gray-100"
                  >
                    <LogOut className="w-5 h-5 text-gray-600" strokeWidth={1.5} />
                    <span className="text-gray-700">로그아웃</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <>
              {!hideNewChat && (
                <Button
                  onClick={() => router.push("/chat/new")}
                  className="bg-gray-900 hover:bg-gray-800 text-white rounded-full px-6"
                >
                  새 채팅
                </Button>
              )}
              <Button
                onClick={() => router.push("/login")}
                variant="outline"
                className="border-2 border-gray-900 bg-white text-gray-900 hover:bg-gray-100 rounded-full px-6"
              >
                로그인
              </Button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
