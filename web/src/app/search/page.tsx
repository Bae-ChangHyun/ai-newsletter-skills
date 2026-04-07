"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { ArticleList, type ArticleListItem } from "@/components/article/ArticleList";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results] = useState<ArticleListItem[]>([]);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="기사 검색..."
          autoFocus
          className="w-full pl-10 pr-4 py-2.5 text-sm bg-muted border border-border rounded-sm focus:outline-none focus:border-accent/50 text-foreground placeholder:text-muted-foreground"
        />
      </div>

      {query && results.length === 0 ? (
        <p className="text-center text-sm text-muted-foreground py-12">
          &ldquo;{query}&rdquo;에 대한 검색 결과가 없습니다.
        </p>
      ) : (
        <ArticleList articles={results} />
      )}
    </div>
  );
}
