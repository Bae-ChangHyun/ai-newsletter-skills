import { db } from "@/lib/db";
import { articles, users, sources, bookmarks, comments } from "@/lib/db/schema";
import { json, error, requireAuth } from "@/lib/api";
import { eq, sql } from "drizzle-orm";

export async function GET() {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const user = await db
    .select({ role: users.role })
    .from(users)
    .where(eq(users.id, userId))
    .limit(1);

  if (user[0]?.role !== "admin") return error("Admin access required", 403);

  const [articleCount] = await db
    .select({ count: sql<number>`count(*)` })
    .from(articles);
  const [userCount] = await db
    .select({ count: sql<number>`count(*)` })
    .from(users);
  const [sourceCount] = await db
    .select({ count: sql<number>`count(*)` })
    .from(sources);
  const [bookmarkCount] = await db
    .select({ count: sql<number>`count(*)` })
    .from(bookmarks);
  const [commentCount] = await db
    .select({ count: sql<number>`count(*)` })
    .from(comments);

  // Articles by state
  const stateBreakdown = await db
    .select({
      state: articles.state,
      count: sql<number>`count(*)`,
    })
    .from(articles)
    .groupBy(articles.state);

  // Top sources by article count
  const topSources = await db
    .select({
      name: sources.name,
      slug: sources.slug,
      count: sql<number>`count(*)`,
    })
    .from(articles)
    .innerJoin(sources, eq(articles.sourceId, sources.id))
    .groupBy(sources.name, sources.slug)
    .orderBy(sql`count(*) desc`)
    .limit(10);

  return json({
    articles: Number(articleCount.count),
    users: Number(userCount.count),
    sources: Number(sourceCount.count),
    bookmarks: Number(bookmarkCount.count),
    comments: Number(commentCount.count),
    stateBreakdown,
    topSources,
  });
}
