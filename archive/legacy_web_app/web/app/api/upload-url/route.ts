import { randomUUID } from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { allowRequest, requestIp } from "@/lib/rate-limit";
import { createUploadUrl } from "@/lib/storage";
import { createUploadToken } from "@/lib/upload-token";
import { ALLOWED_TYPES, MAX_FILE_BYTES } from "@/lib/validation";

export async function POST(req: NextRequest) {
  if (!allowRequest(`upload:${requestIp(req.headers)}`)) {
    return NextResponse.json({ error: "Too many requests. Please wait a minute." }, { status: 429 });
  }
  let body: { contentType?: string; size?: number };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
  const extension = ALLOWED_TYPES[body.contentType as keyof typeof ALLOWED_TYPES];
  if (!extension) {
    return NextResponse.json({ error: "Use an MP4, MOV, or WebM video." }, { status: 400 });
  }
  if (!Number.isFinite(body.size) || body.size! <= 0 || body.size! > MAX_FILE_BYTES) {
    return NextResponse.json({ error: "Video must be smaller than 100 MB." }, { status: 400 });
  }
  const key = `uploads/${randomUUID()}.${extension}`;
  try {
    const uploadUrl = await createUploadUrl(key);
    const uploadToken = createUploadToken({ key, size: body.size!, exp: Date.now() + 15 * 60_000 });
    return NextResponse.json({ uploadUrl, uploadToken, key });
  } catch {
    return NextResponse.json({ error: "Upload service is unavailable." }, { status: 503 });
  }
}
