import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "소스 구독 관리",
};

// Mock source categories
const categories = [
  {
    name: "기업 블로그",
    sources: [
      { name: "OpenAI Blog", slug: "openai-blog", enabled: true },
      { name: "Google AI Blog", slug: "google-ai-blog", enabled: true },
      { name: "HuggingFace Blog", slug: "huggingface-blog", enabled: true },
      { name: "Meta Engineering", slug: "meta-engineering", enabled: true },
      { name: "MS Research", slug: "ms-research", enabled: false },
      { name: "Apple ML", slug: "apple-ml", enabled: false },
      { name: "Amazon Science", slug: "amazon-science", enabled: true },
      { name: "NVIDIA Blog", slug: "nvidia-blog", enabled: true },
    ],
  },
  {
    name: "인기 블로그 / 개인",
    sources: [
      { name: "Simon Willison", slug: "simon-willison", enabled: true },
      { name: "LangChain Blog", slug: "langchain-blog", enabled: true },
    ],
  },
  {
    name: "커뮤니티",
    sources: [
      { name: "Hacker News", slug: "hn", enabled: true },
      { name: "GeekNews", slug: "geeknews", enabled: true },
      { name: "Product Hunt", slug: "producthunt", enabled: false },
      { name: "TLDR AI", slug: "tldr", enabled: true },
      { name: "Reddit", slug: "reddit", enabled: true },
    ],
  },
  {
    name: "릴리즈",
    sources: [
      { name: "PyTorch Releases", slug: "gh-pytorch", enabled: true },
      { name: "Transformers", slug: "gh-transformers", enabled: true },
      { name: "LangChain", slug: "gh-langchain", enabled: true },
      { name: "Ollama", slug: "gh-ollama", enabled: true },
    ],
  },
  {
    name: "한국 커뮤니티",
    sources: [
      { name: "Velopers", slug: "velopers", enabled: true },
      { name: "DevDay", slug: "devday", enabled: true },
    ],
  },
];

export default function SourcesSettingsPage() {
  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div>
        <h1 className="text-lg font-medium text-foreground">소스 구독 관리</h1>
        <p className="text-sm text-muted-foreground mt-1">
          뉴스 피드에 표시할 소스를 선택하세요. 선택하지 않은 소스의 기사는 피드에
          표시되지 않습니다.
        </p>
      </div>

      <div className="space-y-6">
        {categories.map((category) => (
          <div key={category.name} className="space-y-2">
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              {category.name}
            </h2>
            <div className="space-y-0.5">
              {category.sources.map((source) => (
                <label
                  key={source.slug}
                  className="flex items-center gap-3 px-2 py-1.5 rounded-sm hover:bg-muted cursor-pointer transition-colors"
                >
                  <input
                    type="checkbox"
                    defaultChecked={source.enabled}
                    className="rounded-sm border-border text-accent focus:ring-accent/50"
                  />
                  <span className="w-4 h-4 rounded-sm bg-muted flex items-center justify-center text-[9px] font-medium shrink-0">
                    {source.name[0]}
                  </span>
                  <span className="text-sm text-foreground">{source.name}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <button className="px-4 py-2 text-sm font-medium text-accent-foreground bg-accent rounded-sm hover:opacity-90 transition-opacity">
        저장
      </button>
    </div>
  );
}
