"use client";

import { useState } from "react";
import { FeedSortToggle } from "@/components/feed/FeedSortToggle";
import { ArticleList } from "@/components/article/ArticleList";
import { mockArticles } from "@/lib/mock-data";

export function HomeFeed() {
  const [sort, setSort] = useState<"latest" | "score" | "trending">("latest");

  const sorted = [...mockArticles].sort((a, b) => {
    if (sort === "score") return (b.score ?? 0) - (a.score ?? 0);
    if (sort === "trending") return (b.score ?? 0) - (a.score ?? 0);
    return (
      new Date(b.publishedAt ?? 0).getTime() -
      new Date(a.publishedAt ?? 0).getTime()
    );
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <FeedSortToggle value={sort} onChange={setSort} />
      </div>
      <ArticleList articles={sorted} />
    </div>
  );
}
