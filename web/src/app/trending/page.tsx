import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "트렌딩",
};

export default function TrendingPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-4">
      <h1 className="text-lg font-medium text-foreground">트렌딩</h1>
      <p className="text-sm text-muted-foreground">
        지금 빠르게 관심이 높아지고 있는 기사들입니다.
      </p>
      <div className="py-12 text-center text-sm text-muted-foreground">
        데이터 연동 후 표시됩니다.
      </div>
    </div>
  );
}
