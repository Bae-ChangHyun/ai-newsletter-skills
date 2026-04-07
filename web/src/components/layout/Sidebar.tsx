"use client";

import { useState } from "react";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { SourceCategory, Source } from "@/lib/db/schema";

type SourceCategoryWithSources = SourceCategory & { sources: Source[] };

interface SidebarProps {
  categories: SourceCategoryWithSources[];
  selectedSources?: string[];
  onSourceToggle?: (slug: string) => void;
}

export function Sidebar({
  categories,
  selectedSources,
  onSourceToggle,
}: SidebarProps) {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(categories.map((c) => c.slug))
  );

  const toggleCategory = (slug: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  };

  const allSelected =
    !selectedSources || selectedSources.length === 0;

  return (
    <aside className="w-56 shrink-0 hidden lg:block">
      <div className="sticky top-14 py-4 pr-4 space-y-1 max-h-[calc(100vh-3.5rem)] overflow-y-auto">
        <p className="px-2 pb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          소스 필터
        </p>

        <button
          onClick={() => onSourceToggle?.("")}
          className={cn(
            "w-full text-left px-2 py-1.5 text-sm rounded-sm transition-colors",
            allSelected
              ? "text-foreground bg-muted"
              : "text-muted-foreground hover:text-foreground hover:bg-muted"
          )}
        >
          전체 보기
        </button>

        {categories.map((category) => {
          const isExpanded = expandedCategories.has(category.slug);
          return (
            <div key={category.slug}>
              <button
                onClick={() => toggleCategory(category.slug)}
                className="w-full flex items-center gap-1 px-2 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <ChevronRight
                  className={cn(
                    "w-3 h-3 transition-transform",
                    isExpanded && "rotate-90"
                  )}
                />
                <span className="font-medium">{category.name}</span>
                <span className="ml-auto text-xs opacity-50">
                  {category.sources.length}
                </span>
              </button>

              {isExpanded && (
                <div className="ml-4 space-y-0.5">
                  {category.sources.map((source) => {
                    const isActive =
                      allSelected || selectedSources?.includes(source.slug);
                    return (
                      <button
                        key={source.slug}
                        onClick={() => onSourceToggle?.(source.slug)}
                        className={cn(
                          "w-full flex items-center gap-2 px-2 py-1 text-sm rounded-sm transition-colors",
                          isActive
                            ? "text-foreground"
                            : "text-muted-foreground/50"
                        )}
                      >
                        {source.iconUrl ? (
                          <img
                            src={source.iconUrl}
                            alt=""
                            className="w-4 h-4 rounded-sm"
                          />
                        ) : (
                          <span className="w-4 h-4 rounded-sm bg-muted flex items-center justify-center text-[10px] font-medium">
                            {source.name[0]}
                          </span>
                        )}
                        <span className="truncate">{source.name}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </aside>
  );
}
