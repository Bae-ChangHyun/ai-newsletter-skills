import { db } from "@/lib/db";
import { tags } from "@/lib/db/schema";
import { json } from "@/lib/api";
import { desc } from "drizzle-orm";

export async function GET() {
  const rows = await db
    .select()
    .from(tags)
    .orderBy(desc(tags.articleCount));

  // Group by entity_type
  const grouped: Record<string, typeof rows> = {};
  for (const tag of rows) {
    const key = tag.entityType || "other";
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(tag);
  }

  return json({ data: rows, grouped });
}
