import { NextResponse } from "next/server";
import { auth } from "./auth";

export function json<T>(data: T, status = 200) {
  return NextResponse.json(data, { status });
}

export function error(message: string, status = 400) {
  return NextResponse.json({ error: message }, { status });
}

export async function getSession() {
  return auth();
}

export async function requireAuth() {
  const session = await auth();
  if (!session?.user?.id) {
    return null;
  }
  return session;
}

export async function requireAdmin() {
  const session = await auth();
  if (!session?.user?.id) return null;
  // Admin check would query users table for role
  return session;
}

export function parseIntParam(
  value: string | null,
  defaultValue: number,
  min = 1,
  max = Number.MAX_SAFE_INTEGER
): number {
  if (!value) return defaultValue;
  const n = parseInt(value, 10);
  if (isNaN(n)) return defaultValue;
  return Math.max(min, Math.min(max, n));
}
