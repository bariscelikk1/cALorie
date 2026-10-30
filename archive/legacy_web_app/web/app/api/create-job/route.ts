import { randomUUID } from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { Client as QStashClient } from "@upstash/qstash";
import { allowRequest, requestIp } from "@/lib/rate-limit";
import { objectExists } from "@/lib/storage";
import { supabaseAdmin } from "@/lib/supabase";
import { verifyUploadToken } from "@/lib/upload-token";
import { isExercise, isValidStorageKey, isValidWeight } from "@/lib/validation";

export async function POST(req: NextRequest) {
  if (!allowRequest(`job:${requestIp(req.headers)}`, 6)) {
    return NextResponse.json({ error: "Too many analyses. Please wait a minute." }, { status: 429 });
  }
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
  const { videoKey, weightKg, exercise, uploadToken } = body;
  if (
    !isValidStorageKey(videoKey) ||
    !isValidWeight(weightKg) ||
    !isExercise(exercise) ||
    !verifyUploadToken(uploadToken, videoKey)
  ) {
    return NextResponse.json({ error: "Invalid analysis details." }, { status: 400 });
  }
  if (!(await objectExists(videoKey))) {
    return NextResponse.json({ error: "The uploaded video was not found." }, { status: 400 });
  }

  const accessToken = randomUUID();
  const supabase = supabaseAdmin();
  const { data: job, error } = await supabase
    .from("jobs")
    .insert({
      status: "queued",
      video_key: videoKey,
      weight_kg: weightKg,
      exercise,
      access_token: accessToken,
    })
    .select("id")
    .single();
  if (error || !job) {
    return NextResponse.json({ error: "Could not create the analysis job." }, { status: 500 });
  }

  try {
    const qstash = new QStashClient({ token: process.env.QSTASH_TOKEN! });
    await qstash.publishJSON({
      url: `${process.env.WORKER_URL}/process`,
      body: { job_id: job.id, video_key: videoKey },
      retries: 3,
    });
  } catch {
    await supabase
      .from("jobs")
      .update({ status: "error", error_message: "The analysis worker could not be started." })
      .eq("id", job.id);
    return NextResponse.json({ error: "Could not start the analysis worker." }, { status: 503 });
  }
  return NextResponse.json({ jobId: job.id, accessToken });
}
