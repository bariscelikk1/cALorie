import "server-only";
import { createHmac, timingSafeEqual } from "crypto";

type UploadClaim = { key: string; size: number; exp: number };

function secret() {
  const value = process.env.UPLOAD_TOKEN_SECRET;
  if (!value || value.length < 32) throw new Error("UPLOAD_TOKEN_SECRET is not configured");
  return value;
}

export function createUploadToken(claim: UploadClaim) {
  const payload = Buffer.from(JSON.stringify(claim)).toString("base64url");
  const signature = createHmac("sha256", secret()).update(payload).digest("base64url");
  return `${payload}.${signature}`;
}

export function verifyUploadToken(token: unknown, expectedKey: string): UploadClaim | null {
  if (typeof token !== "string") return null;
  const [payload, received] = token.split(".");
  if (!payload || !received) return null;
  const expected = createHmac("sha256", secret()).update(payload).digest("base64url");
  const a = Buffer.from(received);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;
  try {
    const claim = JSON.parse(Buffer.from(payload, "base64url").toString()) as UploadClaim;
    if (claim.key !== expectedKey || claim.exp < Date.now() || claim.size <= 0) return null;
    return claim;
  } catch {
    return null;
  }
}
