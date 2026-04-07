import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "주간 인기",
};

export default function WeeklyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-4">
      <h1 className="text-lg font-medium text-foreground">주간 인기</h1>
      <p className="text-sm text-muted-foreground">
        이번 주 가장 많은 관심을 받은 기사를 모아봤습니다.
      </p>
      <div className="py-12 text-center text-sm text-muted-foreground">
        데이터 연동 후 표시됩니다.
      </div>
    </div>
  );
}
