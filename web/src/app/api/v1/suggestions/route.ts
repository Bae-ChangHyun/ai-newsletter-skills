import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { sourceSuggestions, users } from "@/lib/db/schema";
import { json, error, requireAuth, parseIntParam } from "@/lib/api";
import { eq, desc } from "drizzle-orm";

export async function GET(request: NextRequest) {
  // Admin only
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const user = await db
    .select({ role: users.role })
    .from(users)
    .where(eq(users.id, userId))
    .limit(1);

  if (user[0]?.role !== "admin") return error("Admin access required", 403);

  const params = request.nextUrl.searchParams;
  const page = parseIntParam(params.get("page"), 1);
  const limit = parseIntParam(params.get("limit"), 20, 1, 50);

  const rows = await db
    .select()
    .from(sourceSuggestions)
    .orderBy(desc(sourceSuggestions.createdAt))
    .limit(limit)
    .offset((page - 1) * limit);

  return json({ data: rows });
}

export async function POST(request: NextRequest) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const body = await request.json();
  const name = body.name?.trim();
  const url = body.url?.trim();
  const reason = body.reason?.trim();

  if (!name || !url) return error("name and url are required");

  const userId = parseInt(session.user!.id!, 10);

  const [suggestion] = await db
    .insert(sourceSuggestions)
    .values({ userId, name, url, reason })
    .returning();

  return json(suggestion, 201);
}

export async function PATCH(request: NextRequest) {
  // Admin only - update suggestion status
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const user = await db
    .select({ role: users.role })
    .from(users)
    .where(eq(users.id, userId))
    .limit(1);

  if (user[0]?.role !== "admin") return error("Admin access required", 403);

  const body = await request.json();
  const { id, status, adminNote } = body;

  if (!id || !status) return error("id and status are required");

  const [updated] = await db
    .update(sourceSuggestions)
    .set({ status, adminNote })
    .where(eq(sourceSuggestions.id, id))
    .returning();

  if (!updated) return error("Suggestion not found", 404);

  return json(updated);
}
