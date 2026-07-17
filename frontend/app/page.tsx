"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createRun, runFullPipeline } from "@/lib/api";

const PIPELINE_STEPS = [
  "Technical SEO Agent",
  "AEO Signal Agent",
  "Content Strategy Agent",
  "Competitive Intel Agent",
  "PM Synthesizer Agent",
];

export default function Home() {
  const router = useRouter();
  const [targetUrl, setTargetUrl] = useState("");
  const [competitorUrls, setCompetitorUrls] = useState<string[]>([""]);
  const [buyerQueries, setBuyerQueries] = useState<string[]>([""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function updateAt(list: string[], setList: (v: string[]) => void, index: number, value: string) {
    const next = [...list];
    next[index] = value;
    setList(next);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const cleanCompetitorUrls = competitorUrls.map((u) => u.trim()).filter(Boolean);
    const cleanBuyerQueries = buyerQueries.map((q) => q.trim()).filter(Boolean);

    if (!targetUrl.trim()) {
      setError("Target URL is required.");
      return;
    }
    if (cleanBuyerQueries.length === 0) {
      setError("At least one buyer query is required.");
      return;
    }

    setLoading(true);
    try {
      const run = await createRun({
        target_url: targetUrl.trim(),
        competitor_urls: cleanCompetitorUrls,
        buyer_queries: cleanBuyerQueries,
      });
      await runFullPipeline(run.id);
      router.push(`/report/${run.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong starting the audit.");
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-6 py-24 text-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-border border-t-accent" />
        <div>
          <p className="text-lg font-semibold">Running audit…</p>
          <p className="mt-1 text-sm text-muted">This can take a few seconds while all five agents run.</p>
        </div>
        <ul className="space-y-1 font-mono text-sm text-muted">
          {PIPELINE_STEPS.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold">AEO Product Ops System</h1>
      <p className="mt-2 text-sm text-muted">
        Audit a page for AI-answer-engine visibility and get a prioritized fix roadmap.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-8">
        <div>
          <label htmlFor="target-url" className="block text-sm font-medium">
            Target URL
          </label>
          <input
            id="target-url"
            type="url"
            required
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            placeholder="https://example.com/product"
            className="mt-2 w-full rounded border border-border bg-card px-3 py-2 font-mono text-sm outline-none focus:border-accent"
          />
        </div>

        <div>
          <div className="flex items-center justify-between">
            <span className="block text-sm font-medium">Competitor URLs (optional, up to 3)</span>
            {competitorUrls.length < 3 && (
              <button
                type="button"
                onClick={() => setCompetitorUrls([...competitorUrls, ""])}
                className="text-sm text-accent hover:opacity-80"
              >
                + Add
              </button>
            )}
          </div>
          <div className="mt-2 space-y-2">
            {competitorUrls.map((url, i) => (
              <div key={i} className="flex gap-2">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => updateAt(competitorUrls, setCompetitorUrls, i, e.target.value)}
                  placeholder="https://competitor.com"
                  className="w-full rounded border border-border bg-card px-3 py-2 font-mono text-sm outline-none focus:border-accent"
                />
                {competitorUrls.length > 1 && (
                  <button
                    type="button"
                    onClick={() => setCompetitorUrls(competitorUrls.filter((_, idx) => idx !== i))}
                    className="text-sm text-muted hover:text-not-cited"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <span className="block text-sm font-medium">Buyer queries (1-3)</span>
            {buyerQueries.length < 3 && (
              <button
                type="button"
                onClick={() => setBuyerQueries([...buyerQueries, ""])}
                className="text-sm text-accent hover:opacity-80"
              >
                + Add
              </button>
            )}
          </div>
          <div className="mt-2 space-y-2">
            {buyerQueries.map((query, i) => (
              <div key={i} className="flex gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => updateAt(buyerQueries, setBuyerQueries, i, e.target.value)}
                  placeholder="best project management software for small teams"
                  className="w-full rounded border border-border bg-card px-3 py-2 text-sm outline-none focus:border-accent"
                />
                {buyerQueries.length > 1 && (
                  <button
                    type="button"
                    onClick={() => setBuyerQueries(buyerQueries.filter((_, idx) => idx !== i))}
                    className="text-sm text-muted hover:text-not-cited"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {error && <p className="text-sm text-not-cited">{error}</p>}

        <button
          type="submit"
          className="w-full rounded bg-accent px-4 py-3 font-semibold text-white hover:opacity-90"
        >
          Run Audit
        </button>
      </form>
    </div>
  );
}
