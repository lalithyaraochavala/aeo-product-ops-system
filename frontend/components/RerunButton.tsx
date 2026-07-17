"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { rerun, runFullPipeline } from "@/lib/api";

export default function RerunButton({ runId }: { runId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setError(null);
    setLoading(true);
    try {
      const newRun = await rerun(runId);
      await runFullPipeline(newRun.id);
      router.push(`/report/${newRun.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start re-run.");
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <button
        onClick={handleClick}
        disabled={loading}
        className="text-sm text-accent hover:opacity-80 disabled:opacity-50"
      >
        {loading ? "Running…" : "Re-run for comparison"}
      </button>
      {error && <p className="text-xs text-not-cited">{error}</p>}
    </div>
  );
}
