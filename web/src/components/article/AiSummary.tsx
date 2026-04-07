"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AiSummary as AiSummaryType } from "@/lib/db/schema";

interface AiSummaryProps {
  summary: AiSummaryType;
}

export function AiSummary({ summary }: AiSummaryProps) {
  const [sectionsOpen, setSectionsOpen] = useState(false);

  return (
    <div className="space-y-4">
      {/* Key Takeaways */}
      {summary.key_takeaways?.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            핵심 포인트
          </h4>
          <ul className="space-y-1.5">
            {summary.key_takeaways.map((item, i) => (
              <li
                key={i}
                className="text-sm text-foreground leading-relaxed pl-4 relative before:content-[''] before:absolute before:left-0 before:top-2 before:w-1.5 before:h-1.5 before:rounded-full before:bg-accent/40"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Practical Advice */}
      {summary.practical_advice?.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            실용적 조언
          </h4>
          <ul className="space-y-1.5">
            {summary.practical_advice.map((item, i) => (
              <li
                key={i}
                className="text-sm text-foreground/80 leading-relaxed pl-4 relative before:content-['→'] before:absolute before:left-0 before:text-accent/60"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Section Analysis (collapsible) */}
      {summary.section_analysis?.length > 0 && (
        <div>
          <button
            onClick={() => setSectionsOpen(!sectionsOpen)}
            className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <ChevronDown
              className={cn(
                "w-3 h-3 transition-transform",
                sectionsOpen && "rotate-180"
              )}
            />
            상세 분석 ({summary.section_analysis.length}개 섹션)
          </button>
          {sectionsOpen && (
            <div className="mt-3 space-y-4">
              {summary.section_analysis.map((section, i) => (
                <div key={i}>
                  <h5 className="text-sm font-medium text-foreground mb-1">
                    {section.title}
                  </h5>
                  <p className="text-sm text-foreground/70 leading-relaxed">
                    {section.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Background Terms */}
      {summary.background_terms &&
        Object.keys(summary.background_terms).length > 0 && (
          <div className="pt-2 border-t border-border">
            <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
              배경 용어
            </h4>
            <div className="flex flex-wrap gap-x-4 gap-y-1">
              {Object.entries(summary.background_terms).map(
                ([term, desc]) => (
                  <span key={term} className="text-xs text-muted-foreground">
                    <span className="font-medium text-foreground/80">
                      {term}
                    </span>{" "}
                    — {desc}
                  </span>
                )
              )}
            </div>
          </div>
        )}
    </div>
  );
}
