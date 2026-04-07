import { SourceIcon } from "@/components/source/SourceIcon";
import { timeAgo } from "@/lib/utils";

interface ArticleMetaProps {
  sourceName: string;
  sourceIconUrl?: string | null;
  score?: number | null;
  commentCount?: number | null;
  publishedAt?: string | null;
}

export function ArticleMeta({
  sourceName,
  sourceIconUrl,
  score,
  commentCount,
  publishedAt,
}: ArticleMetaProps) {
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <SourceIcon name={sourceName} iconUrl={sourceIconUrl} />
      <span>{sourceName}</span>
      {typeof score === "number" && score > 0 && (
        <>
          <span className="opacity-30">·</span>
          <span>{score}pt</span>
        </>
      )}
      {typeof commentCount === "number" && commentCount > 0 && (
        <>
          <span className="opacity-30">·</span>
          <span>{commentCount}댓글</span>
        </>
      )}
      {publishedAt && (
        <>
          <span className="opacity-30">·</span>
          <span>{timeAgo(publishedAt)}</span>
        </>
      )}
    </div>
  );
}
