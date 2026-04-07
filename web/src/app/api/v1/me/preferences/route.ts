import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { userSourcePreferences, sources } from "@/lib/db/schema";
import { json, error, requireAuth } from "@/lib/api";
import { eq } from "drizzle-orm";

export async function GET() {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);

  const rows = await db
    .select({
      sourceId: userSourcePreferences.sourceId,
      isEnabled: userSourcePreferences.isEnabled,
      sourceSlug: sources.slug,
      sourceName: sources.name,
    })
    .from(userSourcePreferences)
    .innerJoin(sources, eq(userSourcePreferences.sourceId, sources.id))
    .where(eq(userSourcePreferences.userId, userId));

  return json({ data: rows });
}

export async function PUT(request: NextRequest) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const body = await request.json();

  // body: { preferences: [{ sourceId: number, isEnabled: boolean }] }
  const preferences = body.preferences;
  if (!Array.isArray(preferences)) {
    return error("preferences must be an array");
  }

  // Upsert each preference
  for (const pref of preferences) {
    await db
      .insert(userSourcePreferences)
      .values({
        userId,
        sourceId: pref.sourceId,
        isEnabled: pref.isEnabled,
      })
      .onConflictDoUpdate({
        target: [userSourcePreferences.userId, userSourcePreferences.sourceId],
        set: { isEnabled: pref.isEnabled },
      });
  }

  return json({ updated: preferences.length });
}
