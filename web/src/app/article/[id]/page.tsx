import { ArticleDetail } from "@/components/article/ArticleDetail";
import { mockArticleDetail } from "@/lib/mock-data";

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const article = mockArticleDetail;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <ArticleDetail
        id={parseInt(id)}
        title={article.title}
        titleKo={article.titleKo}
        hookTitleKo={article.hookTitleKo}
        url={article.url}
        sourceName={article.sourceName}
        sourceIconUrl={article.sourceIconUrl}
        score={article.score}
        commentCount={article.commentCount}
        publishedAt={article.publishedAt}
        difficulty={article.difficulty}
        aiSummary={article.aiSummary}
        tags={article.tags}
        relatedArticles={article.relatedArticles}
      />
    </div>
  );
}
