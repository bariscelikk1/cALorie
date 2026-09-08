import { NextRequest, NextResponse } from "next/server";
import { Client as QStashClient } from "@upstash/qstash";
import { supabaseAdmin } from "@/lib/supabase";

export async function POST(req: NextRequest) {
  const { videoKey, weightKg } = await req.json();

  if (!videoKey || typeof weightKg !== "number" || weightKg <= 0) {
    return NextResponse.json({ error: "Missing videoKey or weightKg" }, { status: 400 });
  }

  const supabase = supabaseAdmin();
  const { data: job, error } = await supabase
    .from("jobs")
    .insert({ status: "queued", video_key: videoKey, weight_kg: weightKg })
    .select()
    .single();

  if (error || !job) {
    return NextResponse.json({ error: error?.message ?? "Failed to create job" }, { status: 500 });
  }

  const qstash = new QStashClient({ token: process.env.QSTASH_TOKEN! });
  await qstash.publishJSON({
    url: `${process.env.WORKER_URL}/process`,
    body: { job_id: job.id, video_key: videoKey, weight_kg: weightKg },
  });

  return NextResponse.json({ jobId: job.id });
}
