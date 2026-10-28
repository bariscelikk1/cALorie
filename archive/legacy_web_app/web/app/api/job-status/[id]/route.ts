import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const token = req.nextUrl.searchParams.get("token");
  if (!UUID.test(id) || !token || !UUID.test(token)) {
    return NextResponse.json({ error: "Job not found" }, { status: 404 });
  }
  const { data: job, error } = await supabaseAdmin()
    .from("jobs")
    .select("status, result_json, error_message, video_key, created_at, updated_at")
    .eq("id", id)
    .eq("access_token", token)
    .single();
  if (error || !job) {
    return NextResponse.json({ error: "Job not found" }, { status: 404 });
  }
  const age = Date.now() - new Date(job.updated_at).getTime();
  const stuck = ["queued", "processing"].includes(job.status) && age > 10 * 60_000;
  let videoUrl: string | null = null;
  if (job.status === "done") {
    const { data } = await supabaseAdmin().storage
      .from("workout-videos")
      .createSignedUrl(job.video_key, 60 * 60);
    videoUrl = data?.signedUrl ?? null;
  }
  return NextResponse.json({
    status: stuck ? "error" : job.status,
    result: job.result_json,
    error: stuck ? "Analysis timed out. Please try again." : job.error_message,
    videoUrl,
  });
}
