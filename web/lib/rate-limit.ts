import "server-only";

const attempts = new Map<string, number[]>();

export function allowRequest(key: string, limit = 12, windowMs = 60_000) {
  const now = Date.now();
  const recent = (attempts.get(key) ?? []).filter((time) => now - time < windowMs);
  if (recent.length >= limit) return false;
  recent.push(now);
  attempts.set(key, recent);
  return true;
}

export function requestIp(headers: Headers) {
  return headers.get("x-forwarded-for")?.split(",")[0].trim() ?? "unknown";
}
