import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { bookmarks, articles, sources } from "@/lib/db/schema";
import { json, error, requireAuth, parseIntParam } from "@/lib/api";
import { eq, and, desc, sql } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const params = request.nextUrl.searchParams;
  const page = parseIntParam(params.get("page"), 1);
  const limit = parseIntParam(params.get("limit"), 20, 1, 50);
  const offset = (page - 1) * limit;

  const rows = await db
    .select({
      bookmarkId: bookmarks.id,
      bookmarkedAt: bookmarks.createdAt,
      articleId: articles.id,
      title: articles.title,
      titleKo: articles.titleKo,
      hookTitleKo: articles.hookTitleKo,
      url: articles.url,
      score: articles.score,
      publishedAt: articles.publishedAt,
      sourceName: sources.name,
      sourceSlug: sources.slug,
      sourceIconUrl: sources.iconUrl,
    })
    .from(bookmarks)
    .innerJoin(articles, eq(bookmarks.articleId, articles.id))
    .innerJoin(sources, eq(articles.sourceId, sources.id))
    .where(eq(bookmarks.userId, userId))
    .orderBy(desc(bookmarks.createdAt))
    .limit(limit)
    .offset(offset);

  return json({ data: rows });
}

export async function POST(request: NextRequest) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const body = await request.json();
  const articleId = body.articleId;

  if (!articleId) return error("articleId is required");

  const [bookmark] = await db
    .insert(bookmarks)
    .values({ userId, articleId })
    .onConflictDoNothing()
    .returning();

  // Increment bookmark count
  await db
    .update(articles)
    .set({ bookmarkCount: sql`${articles.bookmarkCount} + 1` })
    .where(eq(articles.id, articleId));

  return json(bookmark || { exists: true }, bookmark ? 201 : 200);
}

export async function DELETE(request: NextRequest) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const params = request.nextUrl.searchParams;
  const articleId = parseInt(params.get("articleId") || "", 10);

  if (isNaN(articleId)) return error("articleId is required");

  const [deleted] = await db
    .delete(bookmarks)
    .where(and(eq(bookmarks.userId, userId), eq(bookmarks.articleId, articleId)))
    .returning();

  if (deleted) {
    await db
      .update(articles)
      .set({
        bookmarkCount: sql`GREATEST(${articles.bookmarkCount} - 1, 0)`,
      })
      .where(eq(articles.id, articleId));
  }

  return json({ deleted: !!deleted });
}
