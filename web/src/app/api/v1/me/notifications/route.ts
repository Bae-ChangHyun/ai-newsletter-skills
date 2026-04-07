import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { notificationSettings } from "@/lib/db/schema";
import { json, error, requireAuth } from "@/lib/api";
import { eq } from "drizzle-orm";

export async function GET() {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);

  const rows = await db
    .select()
    .from(notificationSettings)
    .where(eq(notificationSettings.userId, userId));

  return json({ data: rows });
}

export async function PUT(request: NextRequest) {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const body = await request.json();

  // body: { channel: 'telegram'|'email', isEnabled: boolean, config?: {} }
  const { channel, isEnabled, config } = body;
  if (!channel) return error("channel is required");

  const [result] = await db
    .insert(notificationSettings)
    .values({ userId, channel, isEnabled: !!isEnabled, config: config || {} })
    .onConflictDoUpdate({
      target: [notificationSettings.userId, notificationSettings.channel],
      set: { isEnabled: !!isEnabled, config: config || {} },
    })
    .returning();

  return json(result);
}
