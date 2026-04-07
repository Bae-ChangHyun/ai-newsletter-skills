import { ExternalLink } from "lucide-react";
import { ArticleMeta } from "./ArticleMeta";
import { DifficultyBadge } from "./DifficultyBadge";
import { BookmarkButton } from "./BookmarkButton";
import { AiSummary } from "./AiSummary";
import { TagInline } from "@/components/tag/TagInline";
import type { AiSummary as AiSummaryType } from "@/lib/db/schema";

interface ArticleTag {
  name: string;
  slug: string;
}

interface RelatedArticle {
  id: number;
  hookTitleKo?: string | null;
  title: string;
  sourceName: string;
  sourceIconUrl?: string | null;
}

interface ArticleDetailProps {
  id: number;
  title: string;
  titleKo?: string | null;
  hookTitleKo?: string | null;
  url: string;
  description?: string | null;
  sourceName: string;
  sourceIconUrl?: string | null;
  score?: number | null;
  commentCount?: number | null;
  publishedAt?: string | null;
  difficulty?: string | null;
  aiSummary?: AiSummaryType | null;
  tags?: ArticleTag[];
  relatedArticles?: RelatedArticle[];
  isBookmarked?: boolean;
  onBookmarkToggle?: (id: number) => void;
}

export function ArticleDetail({
  id,
  title,
  titleKo,
  hookTitleKo,
  url,
  sourceName,
  sourceIconUrl,
  score,
  commentCount,
  publishedAt,
  difficulty,
  aiSummary,
  tags = [],
  relatedArticles = [],
  isBookmarked,
  onBookmarkToggle,
}: ArticleDetailProps) {
  return (
    <article className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <h1 className="text-lg font-medium text-foreground leading-snug">
            {hookTitleKo || titleKo || title}
          </h1>
          <BookmarkButton
            articleId={id}
            isBookmarked={isBookmarked}
            onToggle={onBookmarkToggle}
          />
        </div>

        {/* Show original title if different */}
        {hookTitleKo && title !== hookTitleKo && (
          <p className="text-sm text-muted-foreground">{title}</p>
        )}

        <div className="flex items-center gap-3 flex-wrap">
          <ArticleMeta
            sourceName={sourceName}
            sourceIconUrl={sourceIconUrl}
            score={score}
            commentCount={commentCount}
            publishedAt={publishedAt}
          />
          {difficulty && <DifficultyBadge difficulty={difficulty} />}
        </div>
      </div>

      {/* AI Summary */}
      {aiSummary && (
        <div className="py-4 px-4 -mx-4 bg-muted/30 rounded-sm">
          <AiSummary summary={aiSummary} />
        </div>
      )}

      {/* Original Link */}
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-accent-foreground bg-accent rounded-sm hover:opacity-90 transition-opacity"
      >
        원문 읽기
        <ExternalLink className="w-3.5 h-3.5" />
      </a>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap pt-2">
          {tags.map((tag) => (
            <TagInline key={tag.slug} name={tag.name} slug={tag.slug} />
          ))}
        </div>
      )}

      {/* Related Articles */}
      {relatedArticles.length > 0 && (
        <div className="pt-6 border-t border-border space-y-3">
          <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            관련 추천
          </h3>
          <div className="space-y-1">
            {relatedArticles.map((related) => (
              <a
                key={related.id}
                href={`/article/${related.id}`}
                className="flex items-center gap-2 py-1.5 text-sm text-foreground/80 hover:text-foreground transition-colors"
              >
                <span className="w-4 h-4 rounded-sm bg-muted flex items-center justify-center text-[9px] font-medium shrink-0">
                  {related.sourceName[0]}
                </span>
                <span className="truncate">
                  {related.hookTitleKo || related.title}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
