import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { comments } from "@/lib/db/schema";
import { json, error, requireAuth } from "@/lib/api";
import { eq, and } from "drizzle-orm";

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const { id } = await params;
  const commentId = parseInt(id, 10);
  if (isNaN(commentId)) return error("Invalid comment ID", 400);

  const body = await request.json();
  const content = body.content?.trim();
  if (!content) return error("Content is required");

  const userId = parseInt(session.user!.id!, 10);

  const [updated] = await db
    .update(comments)
    .set({ content, updatedAt: new Date() })
    .where(and(eq(comments.id, commentId), eq(comments.userId, userId)))
    .returning();

  if (!updated) return error("Comment not found or not authorized", 404);

  return json(updated);
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const { id } = await params;
  const commentId = parseInt(id, 10);
  if (isNaN(commentId)) return error("Invalid comment ID", 400);

  const userId = parseInt(session.user!.id!, 10);

  // Allow delete by owner (admin check could be added)
  const [deleted] = await db
    .delete(comments)
    .where(and(eq(comments.id, commentId), eq(comments.userId, userId)))
    .returning();

  if (!deleted) return error("Comment not found or not authorized", 404);

  return json({ deleted: true });
}
