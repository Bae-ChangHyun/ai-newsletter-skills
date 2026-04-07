import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { articles, sources } from "@/lib/db/schema";
import { json, parseIntParam } from "@/lib/api";
import { desc, eq, gte, sql } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const limit = parseIntParam(params.get("limit"), 20, 1, 50);

  // Weekly top: last 7 days, sorted by score + bookmarks
  const cutoff = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

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
      viewCount: articles.viewCount,
      publishedAt: articles.publishedAt,
      sourceName: sources.name,
      sourceSlug: sources.slug,
      sourceIconUrl: sources.iconUrl,
    })
    .from(articles)
    .innerJoin(sources, eq(articles.sourceId, sources.id))
    .where(gte(articles.publishedAt, cutoff))
    .orderBy(
      desc(sql`${articles.score} + ${articles.bookmarkCount} * 2`),
      desc(articles.publishedAt)
    )
    .limit(limit);

  return json({ data: rows });
}
