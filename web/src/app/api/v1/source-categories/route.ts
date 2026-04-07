import { db } from "@/lib/db";
import { sourceCategories } from "@/lib/db/schema";
import { json } from "@/lib/api";
import { asc } from "drizzle-orm";

export async function GET() {
  const rows = await db
    .select()
    .from(sourceCategories)
    .orderBy(asc(sourceCategories.displayOrder));

  return json({ data: rows });
}
