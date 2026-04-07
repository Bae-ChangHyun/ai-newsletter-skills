"use client";

import { cn } from "@/lib/utils";

type SortOption = "latest" | "score" | "trending";

const options: { value: SortOption; label: string }[] = [
  { value: "latest", label: "최신순" },
  { value: "score", label: "추천순" },
  { value: "trending", label: "트렌딩" },
];

interface FeedSortToggleProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
}

export function FeedSortToggle({ value, onChange }: FeedSortToggleProps) {
  return (
    <div className="flex items-center gap-0.5">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={cn(
            "px-3 py-1 text-sm transition-colors",
            value === opt.value
              ? "text-foreground border-b-2 border-foreground"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
