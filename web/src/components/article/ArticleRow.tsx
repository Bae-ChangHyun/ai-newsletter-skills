import Link from "next/link";
import { ArticleMeta } from "./ArticleMeta";
import { BookmarkButton } from "./BookmarkButton";
import { DifficultyBadge } from "./DifficultyBadge";
import { TagInline } from "@/components/tag/TagInline";
import { cn } from "@/lib/utils";

interface ArticleTag {
  name: string;
  slug: string;
}

interface ArticleRowProps {
  id: number;
  title: string;
  hookTitleKo?: string | null;
  sourceName: string;
  sourceIconUrl?: string | null;
  score?: number | null;
  commentCount?: number | null;
  publishedAt?: string | null;
  difficulty?: string | null;
  tags?: ArticleTag[];
  isBookmarked?: boolean;
  onBookmarkToggle?: (id: number) => void;
}

export function ArticleRow({
  id,
  title,
  hookTitleKo,
  sourceName,
  sourceIconUrl,
  score,
  commentCount,
  publishedAt,
  difficulty,
  tags = [],
  isBookmarked,
  onBookmarkToggle,
}: ArticleRowProps) {
  const displayTitle = hookTitleKo || title;

  return (
    <div className="group relative border-b border-border">
      <Link
        href={`/article/${id}`}
        className={cn(
          "block px-2 py-3 -mx-2 rounded-sm",
          "hover:bg-muted/50 transition-colors"
        )}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1 space-y-1">
            <h3 className="text-sm font-medium text-foreground leading-snug line-clamp-2">
              {displayTitle}
            </h3>
            <div className="flex items-center gap-2 flex-wrap">
              <ArticleMeta
                sourceName={sourceName}
                sourceIconUrl={sourceIconUrl}
                score={score}
                commentCount={commentCount}
                publishedAt={publishedAt}
              />
              {difficulty && <DifficultyBadge difficulty={difficulty} />}
              {tags.length > 0 && (
                <div className="flex items-center gap-1.5">
                  {tags.slice(0, 3).map((tag) => (
                    <TagInline
                      key={tag.slug}
                      name={tag.name}
                      slug={tag.slug}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
          <BookmarkButton
            articleId={id}
            isBookmarked={isBookmarked}
            onToggle={onBookmarkToggle}
          />
        </div>
      </Link>
    </div>
  );
}
