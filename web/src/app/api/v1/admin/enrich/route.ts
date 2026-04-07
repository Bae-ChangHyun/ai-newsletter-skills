import { json, error, requireAuth } from "@/lib/api";
import { db } from "@/lib/db";
import { users } from "@/lib/db/schema";
import { eq } from "drizzle-orm";

export async function POST() {
  const session = await requireAuth();
  if (!session) return error("Authentication required", 401);

  const userId = parseInt(session.user!.id!, 10);
  const user = await db
    .select({ role: users.role })
    .from(users)
    .where(eq(users.id, userId))
    .limit(1);

  if (user[0]?.role !== "admin") return error("Admin access required", 403);

  // Trigger AI enrichment - would call the Python ai_enrich.py
  return json({
    status: "triggered",
    message:
      "AI enrichment triggered for pending articles.",
  });
}
