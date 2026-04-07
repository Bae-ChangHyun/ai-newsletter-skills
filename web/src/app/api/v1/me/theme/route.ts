import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { users } from "@/lib/db/schema";
import { json, error, requireAuth } from "@/lib/api";
import { eq } from "drizzle-orm";

const VALID_THEMES = ["dark", "light", "system"] as const;

export async function PUT(request: NextRequest) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const body = await request.json();
  const theme = body.theme;

  if (!VALID_THEMES.includes(theme)) {
    return error(`theme must be one of: ${VALID_THEMES.join(", ")}`);
  }

  const userId = parseInt(session.user!.id!, 10);

  await db
    .update(users)
    .set({ theme, updatedAt: new Date() })
    .where(eq(users.id, userId));

  return json({ theme });
}
