import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { comments, users } from "@/lib/db/schema";
import { json, error, requireAuth } from "@/lib/api";
import { eq, asc } from "drizzle-orm";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const articleId = parseInt(id, 10);
  if (isNaN(articleId)) return error("Invalid article ID", 400);

  const rows = await db
    .select({
      id: comments.id,
      content: comments.content,
      parentId: comments.parentId,
      createdAt: comments.createdAt,
      updatedAt: comments.updatedAt,
      userId: users.id,
      userName: users.name,
      userImage: users.image,
    })
    .from(comments)
    .innerJoin(users, eq(comments.userId, users.id))
    .where(eq(comments.articleId, articleId))
    .orderBy(asc(comments.createdAt));

  return json({ data: rows });
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const { id } = await params;
  const articleId = parseInt(id, 10);
  if (isNaN(articleId)) return error("Invalid article ID", 400);

  const body = await request.json();
  const content = body.content?.trim();
  if (!content) return error("Content is required");

  const parentId = body.parentId ? parseInt(body.parentId, 10) : null;

  const [newComment] = await db
    .insert(comments)
    .values({
      articleId,
      userId: parseInt(session.user!.id!, 10),
      parentId,
      content,
    })
    .returning();

  return json(newComment, 201);
}
