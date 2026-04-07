import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "소스 건의",
};

export default function SuggestPage() {
  return (
    <div className="max-w-md mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div>
        <h1 className="text-lg font-medium text-foreground">소스 건의</h1>
        <p className="text-sm text-muted-foreground mt-1">
          수집했으면 하는 뉴스 소스가 있다면 건의해 주세요. 검토 후 추가됩니다.
        </p>
      </div>

      <form className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-foreground">
            소스 이름
          </label>
          <input
            type="text"
            placeholder="예: Anthropic Research Blog"
            className="w-full px-3 py-2 text-sm bg-muted border border-border rounded-sm focus:outline-none focus:border-accent/50 text-foreground placeholder:text-muted-foreground"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium text-foreground">URL</label>
          <input
            type="url"
            placeholder="https://..."
            className="w-full px-3 py-2 text-sm bg-muted border border-border rounded-sm focus:outline-none focus:border-accent/50 text-foreground placeholder:text-muted-foreground"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium text-foreground">
            건의 이유 (선택)
          </label>
          <textarea
            rows={3}
            placeholder="이 소스를 추가하면 좋은 이유를 알려주세요"
            className="w-full px-3 py-2 text-sm bg-muted border border-border rounded-sm focus:outline-none focus:border-accent/50 text-foreground placeholder:text-muted-foreground resize-none"
          />
        </div>

        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-accent-foreground bg-accent rounded-sm hover:opacity-90 transition-opacity"
        >
          건의하기
        </button>
      </form>
    </div>
  );
}
