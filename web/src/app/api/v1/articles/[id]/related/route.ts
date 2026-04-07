import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { articles, sources, articleTags } from "@/lib/db/schema";
import { json, error } from "@/lib/api";
import { desc, eq, ne, inArray, sql } from "drizzle-orm";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const articleId = parseInt(id, 10);
  if (isNaN(articleId)) return error("Invalid article ID", 400);

  // Get the article's source and tags
  const article = await db
    .select({ sourceId: articles.sourceId })
    .from(articles)
    .where(eq(articles.id, articleId))
    .limit(1);

  if (article.length === 0) return error("Article not found", 404);

  const tagIds = await db
    .select({ tagId: articleTags.tagId })
    .from(articleTags)
    .where(eq(articleTags.articleId, articleId));

  // Find related articles by shared tags or same source
  let relatedRows;
  if (tagIds.length > 0) {
    const relatedIds = await db
      .selectDistinct({ articleId: articleTags.articleId })
      .from(articleTags)
      .where(
        inArray(
          articleTags.tagId,
          tagIds.map((t) => t.tagId)
        )
      )
      .limit(20);

    const ids = relatedIds
      .map((r) => r.articleId)
      .filter((rid) => rid !== articleId);

    if (ids.length > 0) {
      relatedRows = await db
        .select({
          id: articles.id,
          title: articles.title,
          hookTitleKo: articles.hookTitleKo,
          url: articles.url,
          score: articles.score,
          publishedAt: articles.publishedAt,
          sourceName: sources.name,
          sourceSlug: sources.slug,
          sourceIconUrl: sources.iconUrl,
        })
        .from(articles)
        .innerJoin(sources, eq(articles.sourceId, sources.id))
        .where(inArray(articles.id, ids))
        .orderBy(desc(articles.score))
        .limit(6);
    }
  }

  // Fallback: same source
  if (!relatedRows || relatedRows.length < 6) {
    const fallback = await db
      .select({
        id: articles.id,
        title: articles.title,
        hookTitleKo: articles.hookTitleKo,
        url: articles.url,
        score: articles.score,
        publishedAt: articles.publishedAt,
        sourceName: sources.name,
        sourceSlug: sources.slug,
        sourceIconUrl: sources.iconUrl,
      })
      .from(articles)
      .innerJoin(sources, eq(articles.sourceId, sources.id))
      .where(eq(articles.sourceId, article[0].sourceId))
      .orderBy(desc(articles.publishedAt))
      .limit(6);

    const existingIds = new Set((relatedRows ?? []).map((r) => r.id));
    const extra = fallback.filter(
      (r) => r.id !== articleId && !existingIds.has(r.id)
    );
    relatedRows = [...(relatedRows ?? []), ...extra].slice(0, 6);
  }

  return json({ data: relatedRows });
}
