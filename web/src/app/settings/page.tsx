import type { Metadata } from "next";
import Link from "next/link";
import { Filter, Bell, Bookmark } from "lucide-react";

export const metadata: Metadata = {
  title: "설정",
};

const settingsLinks = [
  {
    href: "/settings/sources",
    icon: Filter,
    title: "소스 구독 관리",
    description: "뉴스 피드에 표시할 소스를 선택하세요",
  },
  {
    href: "/settings/notifications",
    icon: Bell,
    title: "알림 설정",
    description: "Telegram, 이메일 알림을 설정하세요",
  },
  {
    href: "/settings/bookmarks",
    icon: Bookmark,
    title: "북마크",
    description: "저장한 기사를 확인하세요",
  },
];

export default function SettingsPage() {
  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <h1 className="text-lg font-medium text-foreground">설정</h1>

      <div className="space-y-1">
        {settingsLinks.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 px-3 py-3 rounded-sm hover:bg-muted transition-colors"
          >
            <item.icon className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-sm font-medium text-foreground">
                {item.title}
              </p>
              <p className="text-xs text-muted-foreground">
                {item.description}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
