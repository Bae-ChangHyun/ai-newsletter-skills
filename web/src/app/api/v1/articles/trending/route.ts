import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { articles, sources } from "@/lib/db/schema";
import { json, parseIntParam } from "@/lib/api";
import { desc, eq, gte, sql } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const limit = parseIntParam(params.get("limit"), 30, 1, 50);

  // Trending: high score articles from last 48 hours
  const cutoff = new Date(Date.now() - 48 * 60 * 60 * 1000);

  const rows = await db
    .select({
      id: articles.id,
      title: articles.title,
      titleKo: articles.titleKo,
      hookTitleKo: articles.hookTitleKo,
      url: articles.url,
      score: articles.score,
      commentCount: articles.commentCount,
      bookmarkCount: articles.bookmarkCount,
      publishedAt: articles.publishedAt,
      sourceName: sources.name,
      sourceSlug: sources.slug,
      sourceIconUrl: sources.iconUrl,
    })
    .from(articles)
    .innerJoin(sources, eq(articles.sourceId, sources.id))
    .where(gte(articles.publishedAt, cutoff))
    .orderBy(desc(articles.score), desc(articles.commentCount))
    .limit(limit);

  return json({ data: rows });
}
