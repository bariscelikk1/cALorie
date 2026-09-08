"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [weightKg, setWeightKg] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError("Choose a video first.");
      return;
    }
    const weight = parseFloat(weightKg);
    if (!weight || weight <= 0) {
      setError("Enter your body weight in kg.");
      return;
    }

    setUploading(true);
    try {
      const urlRes = await fetch("/api/upload-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contentType: file.type }),
      });
      if (!urlRes.ok) throw new Error("Could not prepare upload.");
      const { uploadUrl, key } = await urlRes.json();

      const putRes = await fetch(uploadUrl, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });
      if (!putRes.ok) throw new Error("Video upload failed.");

      const jobRes = await fetch("/api/create-job", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoKey: key, weightKg: weight }),
      });
      if (!jobRes.ok) throw new Error("Could not start processing.");
      const { jobId } = await jobRes.json();

      router.push(`/results/${jobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setUploading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md p-8">
      <h1 className="text-2xl font-semibold mb-1">cALorie</h1>
      <p className="text-sm text-neutral-500 mb-6">
        Upload a workout video and get an estimated calorie burn.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Workout video</label>
          <input
            type="file"
            accept="video/mp4,video/quicktime,video/webm"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Body weight (kg)</label>
          <input
            type="number"
            min={1}
            step="0.1"
            value={weightKg}
            onChange={(e) => setWeightKg(e.target.value)}
            className="block w-full rounded border border-neutral-300 px-3 py-2 text-sm"
            placeholder="70"
          />
          <p className="text-xs text-neutral-500 mt-1">
            Needed to estimate calories — the math is weight-dependent.
          </p>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={uploading}
          className="w-full rounded bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {uploading ? "Uploading…" : "Analyze workout"}
        </button>
      </form>
    </main>
  );
}
