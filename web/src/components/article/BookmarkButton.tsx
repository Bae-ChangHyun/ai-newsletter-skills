"use client";

import { Bookmark } from "lucide-react";
import { cn } from "@/lib/utils";

interface BookmarkButtonProps {
  articleId: number;
  isBookmarked?: boolean;
  onToggle?: (articleId: number) => void;
  className?: string;
}

export function BookmarkButton({
  articleId,
  isBookmarked = false,
  onToggle,
  className,
}: BookmarkButtonProps) {
  return (
    <button
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        onToggle?.(articleId);
      }}
      className={cn(
        "p-1 rounded-sm transition-colors",
        isBookmarked
          ? "text-accent"
          : "text-muted-foreground/0 group-hover:text-muted-foreground hover:text-accent",
        className
      )}
      aria-label={isBookmarked ? "Remove bookmark" : "Add bookmark"}
    >
      <Bookmark
        className="w-3.5 h-3.5"
        fill={isBookmarked ? "currentColor" : "none"}
      />
    </button>
  );
}
