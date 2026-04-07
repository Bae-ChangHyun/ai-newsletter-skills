import type { Metadata } from "next";
import Link from "next/link";
import { mockTags } from "@/lib/mock-data";

export const metadata: Metadata = {
  title: "태그",
};

const typeLabels: Record<string, string> = {
  llm: "LLM 모델",
  library: "라이브러리",
  concept: "개념",
  "dev-tool": "개발 도구",
};

export default function TagsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      <h1 className="text-lg font-medium text-foreground">태그</h1>

      {Object.entries(mockTags).map(([type, tagList]) => (
        <div key={type} className="space-y-3">
          <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {typeLabels[type] || type}
          </h2>
          <div className="flex flex-wrap gap-2">
            {tagList.map((tag) => (
              <Link
                key={tag.slug}
                href={`/tags/${tag.slug}`}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 text-sm text-muted-foreground hover:text-foreground hover:bg-muted rounded-sm border border-border transition-colors"
              >
                <span>#{tag.name}</span>
                <span className="text-xs opacity-50">{tag.count}</span>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
