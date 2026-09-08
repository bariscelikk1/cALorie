import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { createUploadUrl } from "@/lib/storage";

const ALLOWED_TYPES = ["video/mp4", "video/quicktime", "video/webm"];

export async function POST(req: NextRequest) {
  const { contentType } = await req.json();

  if (!ALLOWED_TYPES.includes(contentType)) {
    return NextResponse.json({ error: "Unsupported file type" }, { status: 400 });
  }

  const key = `uploads/${randomUUID()}`;
  const uploadUrl = await createUploadUrl(key);

  return NextResponse.json({ uploadUrl, key });
}
