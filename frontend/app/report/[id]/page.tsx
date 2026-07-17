import Link from "next/link";
import LinkedText from "@/components/LinkedText";
import { getReport, getRoadmap, getRun, type Comparison, type Report, type RoadmapItem, type Run } from "@/lib/api";

export default async function ReportPage({ params }: { params: { id: string } }) {
  const { id } = params;

  const run = await getRun(id).catch(() => null);
  if (!run) {
    return (
      <div className="text-center">
        <p className="text-lg font-semibold">Run not found</p>
        <Link href="/" className="mt-4 inline-block text-sm text-accent hover:opacity-80">
          Back to home
        </Link>
      </div>
    );
  }

  const [roadmap, report] = await Promise.all([
    getRoadmap(id).catch(() => [] as RoadmapItem[]),
    getReport(id).catch(() => null as Report | null),
  ]);

  return (
    <div className="space-y-10">
      <div>
        <p className="font-mono text-sm text-muted">{run.target_url}</p>
        <div className="mt-1 flex items-center gap-3">
          <h1 className="text-2xl font-semibold">Report</h1>
          <StatusBadge status={run.status} />
        </div>
        <p className="mt-1 text-xs text-muted">
          Run {run.id} · {new Date(run.created_at).toLocaleString()}
        </p>
      </div>

      {report?.comparison && <ComparisonSection comparison={report.comparison} />}

      {report && (
        <section>
          <h2 className="text-lg font-semibold">Stakeholder Summary</h2>
          <div className="mt-3 rounded border border-accent/40 bg-card px-5 py-4">
            <p className="text-sm leading-relaxed">
              <LinkedText text={report.stakeholder_summary} />
            </p>
          </div>
        </section>
      )}

      <section>
        <h2 className="text-lg font-semibold">RICE-Scored Roadmap</h2>
        {roadmap.length === 0 ? (
          <p className="mt-3 text-sm text-muted">No roadmap items yet — the synthesis step may not have run.</p>
        ) : (
          <div className="mt-3 overflow-x-auto rounded border border-border">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-border bg-card text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">Reach</th>
                  <th className="px-4 py-3 font-medium">Impact</th>
                  <th className="px-4 py-3 font-medium">Confidence</th>
                  <th className="px-4 py-3 font-medium">Effort</th>
                  <th className="px-4 py-3 font-medium">RICE</th>
                </tr>
              </thead>
              <tbody>
                {roadmap.map((item) => (
                  <tr key={item.id} className="border-b border-border last:border-0">
                    <td className="px-4 py-3">
                      <p className="font-medium">
                        <LinkedText text={item.title} />
                      </p>
                      <p className="mt-1 text-xs text-muted">
                        <LinkedText text={item.description} />
                      </p>
                    </td>
                    <td className="px-4 py-3 font-mono">{item.reach}</td>
                    <td className="px-4 py-3 font-mono">{item.impact}</td>
                    <td className="px-4 py-3 font-mono">{item.confidence}</td>
                    <td className="px-4 py-3 font-mono">{item.effort}</td>
                    <td className="px-4 py-3 font-mono font-semibold text-accent">{item.rice_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {report && (
        <section>
          <h2 className="text-lg font-semibold">One-Page PRD: {report.prd.title}</h2>
          <div className="mt-3 space-y-4 rounded border border-border bg-card px-5 py-4">
            <PrdField label="Problem Statement" text={report.prd.problem_statement} />
            <PrdField label="Proposed Solution" text={report.prd.proposed_solution} />
            <PrdField label="Success Metric" text={report.prd.success_metric} />
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted">In Scope</p>
                <ul className="mt-1 list-inside list-disc text-sm">
                  {report.prd.scope_in.map((item, i) => (
                    <li key={i}>
                      <LinkedText text={item} />
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted">Out of Scope</p>
                <ul className="mt-1 list-inside list-disc text-sm">
                  {report.prd.scope_out.map((item, i) => (
                    <li key={i}>
                      <LinkedText text={item} />
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>
      )}

      {!report && (
        <p className="text-sm text-muted">
          No synthesis report is available for this run yet — the PM Synthesizer step may not have completed.
        </p>
      )}
    </div>
  );
}

function PrdField({ label, text }: { label: string; text: string }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-1 text-sm leading-relaxed">
        <LinkedText text={text} />
      </p>
    </div>
  );
}

function ComparisonSection({ comparison }: { comparison: Comparison }) {
  const beforePct = Math.round(comparison.citation_rate_before * 100);
  const afterPct = Math.round(comparison.citation_rate_after * 100);

  return (
    <section>
      <h2 className="text-lg font-semibold">Before / After Comparison</h2>
      <p className="mt-1 text-xs text-muted">
        Compared against{" "}
        <Link href={`/report/${comparison.parent_run_id}`} className="text-accent hover:underline">
          the original run
        </Link>
      </p>

      <div className="mt-3 space-y-3 rounded border border-border bg-card px-5 py-4">
        <CitationBar label="Before" percent={beforePct} />
        <CitationBar label="After" percent={afterPct} />
      </div>

      <div className="mt-4 rounded border border-border bg-card px-5 py-4">
        <p className="text-xs font-medium uppercase tracking-wide text-muted">Original Roadmap Progress</p>
        <ul className="mt-2 space-y-2 text-sm">
          {comparison.parent_roadmap.map((item) => (
            <li key={item.id} className="flex items-center gap-2">
              {item.status === "resolved" ? (
                <span className="text-cited">✓</span>
              ) : (
                <span className="text-muted">○</span>
              )}
              <span className={item.status === "resolved" ? "text-muted line-through" : ""}>
                <LinkedText text={item.title} />
              </span>
              <span className="text-xs text-muted">({item.status})</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function CitationBar({ label, percent }: { label: string; percent: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs text-muted">
        <span>{label}</span>
        <span className="font-mono">{percent}%</span>
      </div>
      <div className="mt-1 h-3 w-full overflow-hidden rounded bg-border">
        <div className="h-full rounded bg-accent" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: Run["status"] }) {
  const styles: Record<Run["status"], string> = {
    complete: "bg-cited/15 text-cited",
    partial: "bg-accent/15 text-accent",
    failed: "bg-not-cited/15 text-not-cited",
    running: "bg-muted/20 text-muted",
    pending: "bg-muted/20 text-muted",
  };
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-medium ${styles[status]}`}>{status}</span>
  );
}
