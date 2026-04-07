import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { articles, sources, articleTags, tags } from "@/lib/db/schema";
import { json, error } from "@/lib/api";
import { eq, sql } from "drizzle-orm";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const articleId = parseInt(id, 10);
  if (isNaN(articleId)) return error("Invalid article ID", 400);

  const rows = await db
    .select({
      id: articles.id,
      title: articles.title,
      titleKo: articles.titleKo,
      hookTitleKo: articles.hookTitleKo,
      url: articles.url,
      canonicalUrl: articles.canonicalUrl,
      description: articles.description,
      score: articles.score,
      commentCount: articles.commentCount,
      viewCount: articles.viewCount,
      bookmarkCount: articles.bookmarkCount,
      duplicateCount: articles.duplicateCount,
      externalSource: articles.externalSource,
      state: articles.state,
      difficulty: articles.difficulty,
      aiCategory: articles.aiCategory,
      contentType: articles.contentType,
      aiSummaryJson: articles.aiSummaryJson,
      summaryStatus: articles.summaryStatus,
      hasConcreteEvidence: articles.hasConcreteEvidence,
      publishedAt: articles.publishedAt,
      firstSeenAt: articles.firstSeenAt,
      createdAt: articles.createdAt,
      sourceName: sources.name,
      sourceSlug: sources.slug,
      sourceIconUrl: sources.iconUrl,
      sourceTier: sources.displayTier,
    })
    .from(articles)
    .innerJoin(sources, eq(articles.sourceId, sources.id))
    .where(eq(articles.id, articleId))
    .limit(1);

  if (rows.length === 0) return error("Article not found", 404);

  // Increment view count
  await db
    .update(articles)
    .set({ viewCount: sql`${articles.viewCount} + 1` })
    .where(eq(articles.id, articleId));

  // Fetch tags
  const articleTagRows = await db
    .select({ name: tags.name, slug: tags.slug, entityType: tags.entityType })
    .from(articleTags)
    .innerJoin(tags, eq(articleTags.tagId, tags.id))
    .where(eq(articleTags.articleId, articleId));

  return json({
    ...rows[0],
    tags: articleTagRows,
  });
}
