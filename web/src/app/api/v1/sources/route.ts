import { db } from "@/lib/db";
import { sources, sourceCategories, articles } from "@/lib/db/schema";
import { json } from "@/lib/api";
import { eq, sql, asc } from "drizzle-orm";

export async function GET() {
  // Get sources grouped by category with article counts
  const rows = await db
    .select({
      id: sources.id,
      slug: sources.slug,
      name: sources.name,
      type: sources.type,
      displayTier: sources.displayTier,
      url: sources.url,
      iconUrl: sources.iconUrl,
      description: sources.description,
      isActive: sources.isActive,
      categoryId: sourceCategories.id,
      categorySlug: sourceCategories.slug,
      categoryName: sourceCategories.name,
      categoryOrder: sourceCategories.displayOrder,
      articleCount: sql<number>`(
        SELECT count(*) FROM articles WHERE articles.source_id = ${sources.id}
      )`,
    })
    .from(sources)
    .leftJoin(sourceCategories, eq(sources.categoryId, sourceCategories.id))
    .where(eq(sources.isActive, true))
    .orderBy(asc(sourceCategories.displayOrder), asc(sources.name));

  // Group by category
  const grouped: Record<
    string,
    {
      category: { id: number; slug: string; name: string; order: number };
      sources: typeof rows;
    }
  > = {};

  for (const row of rows) {
    const catKey = row.categorySlug || "uncategorized";
    if (!grouped[catKey]) {
      grouped[catKey] = {
        category: {
          id: row.categoryId ?? 0,
          slug: catKey,
          name: row.categoryName || "기타",
          order: row.categoryOrder ?? 99,
        },
        sources: [],
      };
    }
    grouped[catKey].sources.push(row);
  }

  const data = Object.values(grouped).sort(
    (a, b) => a.category.order - b.category.order
  );

  return json({ data });
}
