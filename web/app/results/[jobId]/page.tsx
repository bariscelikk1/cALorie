"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type JobStatus = "queued" | "processing" | "done" | "error";

type Result = {
  calories_low: number;
  calories_high: number;
  confidence: "low" | "medium" | "high";
  note?: string;
};

export default function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [status, setStatus] = useState<JobStatus>("queued");
  const [result, setResult] = useState<Result | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const res = await fetch(`/api/job-status/${jobId}`);
      if (!res.ok || cancelled) return;
      const data = await res.json();
      if (cancelled) return;

      setStatus(data.status);
      if (data.status === "done") {
        setResult(data.result);
        return;
      }
      setTimeout(poll, 2000);
    }

    poll();
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  return (
    <main className="mx-auto max-w-md p-8">
      <h1 className="text-2xl font-semibold mb-6">Your results</h1>

      {status !== "done" && (
        <p className="text-neutral-600">
          {status === "queued" ? "Queued…" : "Analyzing your video…"}
        </p>
      )}

      {status === "done" && result && (
        <div className="space-y-3">
          <p className="text-4xl font-bold">
            {result.calories_low}–{result.calories_high} kcal
          </p>
          <p className="text-sm text-neutral-500">
            Confidence: <span className="font-medium">{result.confidence}</span>
          </p>
          <p className="text-xs text-neutral-400">
            This is an estimate based on video and body weight, not a medical
            measurement.
          </p>
          {result.note && (
            <p className="text-xs text-amber-600">{result.note}</p>
          )}
        </div>
      )}
    </main>
  );
}
