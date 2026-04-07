import { ArticleRow } from "./ArticleRow";

interface ArticleTag {
  name: string;
  slug: string;
}

export interface ArticleListItem {
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
}

interface ArticleListProps {
  articles: ArticleListItem[];
  onBookmarkToggle?: (id: number) => void;
}

export function ArticleList({ articles, onBookmarkToggle }: ArticleListProps) {
  if (articles.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">
        표시할 기사가 없습니다.
      </div>
    );
  }

  return (
    <div>
      {articles.map((article) => (
        <ArticleRow
          key={article.id}
          {...article}
          onBookmarkToggle={onBookmarkToggle}
        />
      ))}
    </div>
  );
}
