import { Suspense } from "react";
import { HomeFeed } from "./home-feed";
import { ArticleListSkeleton } from "@/components/common/Skeleton";

export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6">
      <div className="flex gap-6">
        {/* Sidebar placeholder - will connect to real data */}
        <aside className="w-56 shrink-0 hidden lg:block">
          <div className="sticky top-14 py-4 pr-4 space-y-1">
            <p className="px-2 pb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
              소스 필터
            </p>
            <SidebarPlaceholder />
          </div>
        </aside>

        {/* Main feed */}
        <div className="flex-1 min-w-0 py-4">
          <Suspense fallback={<ArticleListSkeleton />}>
            <HomeFeed />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

function SidebarPlaceholder() {
  const categories = [
    {
      name: "기업 블로그",
      sources: ["OpenAI Blog", "Google AI", "HuggingFace", "Meta Engineering"],
    },
    {
      name: "커뮤니티",
      sources: ["Hacker News", "GeekNews", "Reddit", "Product Hunt"],
    },
    {
      name: "릴리즈",
      sources: ["PyTorch", "Transformers", "LangChain", "Ollama"],
    },
    { name: "한국 커뮤니티", sources: ["Velopers", "DevDay"] },
  ];

  return (
    <div className="space-y-1">
      <button className="w-full text-left px-2 py-1.5 text-sm text-foreground bg-muted rounded-sm">
        전체 보기
      </button>
      {categories.map((cat) => (
        <div key={cat.name}>
          <p className="px-2 py-1.5 text-sm font-medium text-muted-foreground">
            {cat.name}
          </p>
          <div className="ml-4 space-y-0.5">
            {cat.sources.map((src) => (
              <button
                key={src}
                className="w-full flex items-center gap-2 px-2 py-1 text-sm text-foreground rounded-sm hover:bg-muted transition-colors"
              >
                <span className="w-4 h-4 rounded-sm bg-muted flex items-center justify-center text-[9px] font-medium">
                  {src[0]}
                </span>
                <span className="truncate">{src}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
