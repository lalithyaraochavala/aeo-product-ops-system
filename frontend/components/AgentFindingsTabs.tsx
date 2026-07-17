"use client";

import { useState } from "react";
import LinkedText from "@/components/LinkedText";
import type {
  AeoSignalOutput,
  AgentFinding,
  AgentFindings,
  CompetitiveIntelOutput,
  ContentStrategyOutput,
  TechnicalSeoOutput,
} from "@/lib/api";

const TABS = [
  { key: "technical_seo", label: "Technical SEO", hint: "How well the page's code/markup helps AI understand it" },
  { key: "aeo_signal", label: "AEO Signal", hint: "Whether real AI search tools actually cite this page" },
  { key: "content_strategy", label: "Content Strategy", hint: "Specific writing/content changes recommended" },
  { key: "competitive_intel", label: "Competitive Intel", hint: "How this compares to the competitors you listed" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function AgentFindingsTabs({ findings }: { findings: AgentFindings }) {
  const [active, setActive] = useState<TabKey>("technical_seo");

  return (
    <section>
      <h2 className="text-lg font-semibold">Agent Findings</h2>
      <p className="mt-1 text-xs text-muted">
        The detailed technical results behind the summary above, organized by specialist.
      </p>
      <div className="mt-3 flex flex-wrap gap-1 border-b border-border">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActive(tab.key)}
            title={tab.hint}
            className={`rounded-t px-4 py-2 text-sm font-medium ${
              active === tab.key
                ? "border-b-2 border-accent text-accent"
                : "text-muted hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="rounded-b border border-t-0 border-border bg-card px-5 py-4">
        {active === "technical_seo" && <TechnicalSeoPanel finding={findings.technical_seo} />}
        {active === "aeo_signal" && <AeoSignalPanel finding={findings.aeo_signal} />}
        {active === "content_strategy" && <ContentStrategyPanel finding={findings.content_strategy} />}
        {active === "competitive_intel" && <CompetitiveIntelPanel finding={findings.competitive_intel} />}
      </div>
    </section>
  );
}

function ErrorOrMissing({ finding }: { finding: AgentFinding<unknown> }) {
  if (finding === null) {
    return <p className="text-sm text-muted">This agent hasn&apos;t run for this run yet.</p>;
  }
  const message =
    finding.raw_output && typeof finding.raw_output === "object" && "error" in finding.raw_output
      ? String((finding.raw_output as { error: string }).error)
      : "This agent failed to produce findings for this run.";
  return (
    <div className="rounded border border-not-cited/40 bg-not-cited/10 px-4 py-3">
      <p className="text-sm text-not-cited">✗ {message}</p>
    </div>
  );
}

function SeverityBadge({ severity }: { severity: "high" | "medium" | "low" }) {
  const styles = {
    high: "bg-not-cited/15 text-not-cited",
    medium: "bg-accent/15 text-accent",
    low: "bg-muted/20 text-muted",
  };
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-medium uppercase ${styles[severity]}`}>{severity}</span>
  );
}

function TechnicalSeoPanel({ finding }: { finding: AgentFinding<TechnicalSeoOutput> }) {
  if (finding === null || finding.status !== "success") return <ErrorOrMissing finding={finding} />;
  const output = finding.raw_output as TechnicalSeoOutput;
  const { raw_findings } = output;

  return (
    <div className="space-y-5">
      <div>
        <p className="font-mono text-2xl font-semibold text-accent">{output.score}/100</p>
        <p className="mt-1 text-sm text-muted">{output.summary}</p>
      </div>

      {output.issues.length > 0 && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted">Issues</p>
          <ul className="mt-2 space-y-3">
            {output.issues.map((issue, i) => (
              <li key={i} className="rounded border border-border px-3 py-2">
                <div className="flex items-center gap-2">
                  <SeverityBadge severity={issue.severity} />
                  <span className="text-sm font-medium">{issue.issue}</span>
                </div>
                <p className="mt-1 text-sm text-muted">{issue.recommendation}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted">Raw Findings</p>
        <p className="mt-1 text-xs text-muted">
          JSON-LD is a small block of code that tells AI tools what a page is about — its absence is a common
          reason pages don&apos;t get cited.
        </p>
        <dl className="mt-2 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          <div className="flex justify-between sm:block">
            <dt className="text-muted" title="A code block that clearly labels what the page is about for AI/search tools">
              JSON-LD present
            </dt>
            <dd className="font-mono">{raw_findings.json_ld_present ? "yes" : "no"}</dd>
          </div>
          <div className="flex justify-between sm:block">
            <dt className="text-muted">JSON-LD types</dt>
            <dd className="font-mono">
              {raw_findings.json_ld_types.length > 0 ? raw_findings.json_ld_types.join(", ") : "none"}
            </dd>
          </div>
          <div className="flex justify-between sm:block">
            <dt className="text-muted">Title tag</dt>
            <dd className="font-mono">{raw_findings.title ?? "(none)"}</dd>
          </div>
          <div className="flex justify-between sm:block">
            <dt className="text-muted">Meta description</dt>
            <dd className="font-mono">{raw_findings.meta_description ?? "(none)"}</dd>
          </div>
          <div className="flex justify-between sm:block">
            <dt className="text-muted">H1 count</dt>
            <dd className="font-mono">{raw_findings.h1_count}</dd>
          </div>
          <div className="flex justify-between sm:block">
            <dt className="text-muted">H2 count</dt>
            <dd className="font-mono">{raw_findings.h2_count}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

function CitedBadge({ cited }: { cited: boolean }) {
  return cited ? (
    <span className="whitespace-nowrap text-cited">✓ Cited</span>
  ) : (
    <span className="whitespace-nowrap text-not-cited">✗ Not cited</span>
  );
}

function AeoSignalPanel({ finding }: { finding: AgentFinding<AeoSignalOutput> }) {
  if (finding === null || finding.status !== "success") return <ErrorOrMissing finding={finding} />;
  const output = finding.raw_output as AeoSignalOutput;
  const citedCount = output.query_results.filter((q) => q.target_cited).length;
  const total = output.query_results.length;

  return (
    <div className="space-y-5">
      <p className="text-sm">
        <span className="font-mono text-lg font-semibold text-accent">
          {citedCount} of {total}
        </span>{" "}
        queries cited ({Math.round(output.citation_rate * 100)}%)
      </p>

      <div className="space-y-4">
        {output.query_results.map((q, i) => (
          <div key={i} className="rounded border border-border px-3 py-3">
            <p className="text-sm font-medium">&ldquo;{q.query}&rdquo;</p>
            <div className="mt-2 flex items-start gap-2 text-sm">
              <CitedBadge cited={q.target_cited} />
              <span className="text-muted">
                <LinkedText text={q.target_reasoning} />
              </span>
            </div>
            {q.competitors.length > 0 && (
              <ul className="mt-2 space-y-1 border-l border-border pl-3">
                {q.competitors.map((c, j) => (
                  <li key={j} className="flex items-start gap-2 text-xs">
                    <CitedBadge cited={c.cited} />
                    <span className="font-mono text-muted">{c.url}</span>
                    <span className="text-muted">
                      <LinkedText text={c.reasoning} />
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ContentStrategyPanel({ finding }: { finding: AgentFinding<ContentStrategyOutput> }) {
  if (finding === null || finding.status !== "success") return <ErrorOrMissing finding={finding} />;
  const output = finding.raw_output as ContentStrategyOutput;

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted">{output.summary}</p>
      <ul className="space-y-3">
        {output.recommendations.map((rec, i) => (
          <li key={i} className="rounded border border-border px-3 py-2">
            <p className="text-sm font-medium">
              <LinkedText text={rec.recommendation} />
            </p>
            <p className="mt-1 text-xs text-muted">
              Based on: <LinkedText text={rec.based_on} />
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

function CompetitiveIntelPanel({ finding }: { finding: AgentFinding<CompetitiveIntelOutput> }) {
  if (finding === null || finding.status !== "success") return <ErrorOrMissing finding={finding} />;
  const output = finding.raw_output as CompetitiveIntelOutput;
  const entries = Object.entries(output.citation_share).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted">Citation Share</p>
        <div className="mt-2 space-y-2">
          {entries.map(([domain, share]) => (
            <div key={domain}>
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-muted">{domain}</span>
                <span className="font-mono">{Math.round(share * 100)}%</span>
              </div>
              <div className="mt-1 h-2 w-full overflow-hidden rounded bg-border">
                <div className="h-full rounded bg-accent" style={{ width: `${Math.round(share * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {output.queries_losing.length > 0 && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted">Queries Losing</p>
          <ul className="mt-2 space-y-1 text-sm">
            {output.queries_losing.map((q, i) => (
              <li key={i}>
                &ldquo;{q.query}&rdquo; — won by <span className="font-mono">{q.winning_competitors.join(", ")}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted">Narrative</p>
        <p className="mt-1 text-sm">
          <LinkedText text={output.narrative} />
        </p>
      </div>
    </div>
  );
}
