import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { articles, sources, sourceCategories } from "@/lib/db/schema";
import { json, error, parseIntParam } from "@/lib/api";
import { desc, eq, and, inArray, gte, sql, ilike, or } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;

  const page = parseIntParam(params.get("page"), 1);
  const limit = parseIntParam(params.get("limit"), 20, 1, 50);
  const offset = (page - 1) * limit;

  const sourceFilter = params.get("source");
  const sourceCategoryFilter = params.get("source_category");
  const difficulty = params.get("difficulty");
  const category = params.get("category");
  const sort = params.get("sort") || "latest";
  const since = params.get("since");
  const q = params.get("q");

  const conditions: ReturnType<typeof eq>[] = [];

  // Source filter (by slug)
  if (sourceFilter) {
    const slugs = sourceFilter.split(",").map((s) => s.trim());
    const matchedSources = await db
      .select({ id: sources.id })
      .from(sources)
      .where(inArray(sources.slug, slugs));
    if (matchedSources.length > 0) {
      conditions.push(
        inArray(
          articles.sourceId,
          matchedSources.map((s) => s.id)
        )
      );
    }
  }

  // Source category filter
  if (sourceCategoryFilter) {
    const catSlugs = sourceCategoryFilter.split(",").map((s) => s.trim());
    const matchedCats = await db
      .select({ id: sourceCategories.id })
      .from(sourceCategories)
      .where(inArray(sourceCategories.slug, catSlugs));
    if (matchedCats.length > 0) {
      const catIds = matchedCats.map((c) => c.id);
      const matchedSources = await db
        .select({ id: sources.id })
        .from(sources)
        .where(inArray(sources.categoryId, catIds));
      if (matchedSources.length > 0) {
        conditions.push(
          inArray(
            articles.sourceId,
            matchedSources.map((s) => s.id)
          )
        );
      }
    }
  }

  if (difficulty) {
    conditions.push(eq(articles.difficulty, difficulty));
  }

  if (category) {
    conditions.push(eq(articles.aiCategory, category));
  }

  if (since) {
    const sinceDate = new Date(since);
    if (!isNaN(sinceDate.getTime())) {
      conditions.push(gte(articles.publishedAt, sinceDate));
    }
  }

  if (q) {
    conditions.push(
      or(
        ilike(articles.title, `%${q}%`),
        ilike(articles.titleKo, `%${q}%`),
        ilike(articles.hookTitleKo, `%${q}%`),
        ilike(articles.description, `%${q}%`)
      )!
    );
  }

  // Sort
  const orderBy =
    sort === "score"
      ? [desc(articles.score)]
      : sort === "comments"
        ? [desc(articles.commentCount)]
        : sort === "trending"
          ? [desc(articles.score), desc(articles.publishedAt)]
          : [desc(articles.publishedAt)];

  const where = conditions.length > 0 ? and(...conditions) : undefined;

  const [rows, countResult] = await Promise.all([
    db
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
        externalSource: articles.externalSource,
        state: articles.state,
        difficulty: articles.difficulty,
        aiCategory: articles.aiCategory,
        summaryStatus: articles.summaryStatus,
        publishedAt: articles.publishedAt,
        createdAt: articles.createdAt,
        sourceId: articles.sourceId,
        sourceName: sources.name,
        sourceSlug: sources.slug,
        sourceIconUrl: sources.iconUrl,
        sourceTier: sources.displayTier,
      })
      .from(articles)
      .innerJoin(sources, eq(articles.sourceId, sources.id))
      .where(where)
      .orderBy(...orderBy)
      .limit(limit)
      .offset(offset),
    db
      .select({ count: sql<number>`count(*)` })
      .from(articles)
      .where(where),
  ]);

  const total = Number(countResult[0]?.count ?? 0);

  return json({
    data: rows,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  });
}
