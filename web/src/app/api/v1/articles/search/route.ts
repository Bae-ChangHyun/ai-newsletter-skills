import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { articles, sources } from "@/lib/db/schema";
import { json, error, parseIntParam } from "@/lib/api";
import { desc, eq, or, ilike, sql } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const q = params.get("q");
  if (!q || q.trim().length === 0) return error("Query parameter 'q' is required");

  const page = parseIntParam(params.get("page"), 1);
  const limit = parseIntParam(params.get("limit"), 20, 1, 50);
  const offset = (page - 1) * limit;

  const searchCondition = or(
    ilike(articles.title, `%${q}%`),
    ilike(articles.titleKo, `%${q}%`),
    ilike(articles.hookTitleKo, `%${q}%`),
    ilike(articles.description, `%${q}%`)
  )!;

  const [rows, countResult] = await Promise.all([
    db
      .select({
        id: articles.id,
        title: articles.title,
        titleKo: articles.titleKo,
        hookTitleKo: articles.hookTitleKo,
        url: articles.url,
        description: articles.description,
        score: articles.score,
        publishedAt: articles.publishedAt,
        sourceName: sources.name,
        sourceSlug: sources.slug,
        sourceIconUrl: sources.iconUrl,
      })
      .from(articles)
      .innerJoin(sources, eq(articles.sourceId, sources.id))
      .where(searchCondition)
      .orderBy(desc(articles.score))
      .limit(limit)
      .offset(offset),
    db
      .select({ count: sql<number>`count(*)` })
      .from(articles)
      .where(searchCondition),
  ]);

  return json({
    data: rows,
    pagination: {
      page,
      limit,
      total: Number(countResult[0]?.count ?? 0),
      totalPages: Math.ceil(Number(countResult[0]?.count ?? 0) / limit),
    },
  });
}
