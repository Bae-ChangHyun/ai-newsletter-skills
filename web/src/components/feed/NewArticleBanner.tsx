"use client";

import { RefreshCw } from "lucide-react";

interface NewArticleBannerProps {
  count: number;
  onRefresh: () => void;
}

export function NewArticleBanner({ count, onRefresh }: NewArticleBannerProps) {
  if (count <= 0) return null;

  return (
    <button
      onClick={onRefresh}
      className="w-full py-2 text-sm text-accent bg-accent/5 border border-accent/10 rounded-sm hover:bg-accent/10 transition-colors flex items-center justify-center gap-1.5"
    >
      <RefreshCw className="w-3 h-3" />
      새 글 {count}개
    </button>
  );
}
