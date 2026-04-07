import type { Metadata } from "next";
import { Bookmark } from "lucide-react";

export const metadata: Metadata = {
  title: "북마크",
};

export default function BookmarksPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-4">
      <h1 className="text-lg font-medium text-foreground">북마크</h1>
      <p className="text-sm text-muted-foreground">
        저장한 기사를 여기서 확인할 수 있습니다.
      </p>

      {/* Empty state */}
      <div className="py-16 text-center space-y-3">
        <Bookmark className="w-8 h-8 text-muted-foreground/30 mx-auto" />
        <p className="text-sm text-muted-foreground">
          아직 북마크한 기사가 없습니다.
        </p>
        <p className="text-xs text-muted-foreground/60">
          기사 목록에서 북마크 아이콘을 클릭하여 저장하세요.
        </p>
      </div>
    </div>
  );
}
