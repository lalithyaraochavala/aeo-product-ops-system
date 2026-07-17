import type { ReactNode } from "react";
import LinkedText from "@/components/LinkedText";

type Standing = "leading" | "tied" | "behind" | "unknown";

function computeStanding(citationShare: Record<string, number> | null, targetDomain: string): Standing {
  if (!citationShare) return "unknown";
  const entries = Object.entries(citationShare);
  const targetShare = citationShare[targetDomain];
  const others = entries.filter(([domain]) => domain !== targetDomain).map(([, share]) => share);
  if (targetShare === undefined || others.length === 0) return "unknown";

  const othersMax = Math.max(...others);
  if (targetShare > othersMax) return "leading";
  if (targetShare === othersMax) return "tied";
  return "behind";
}

const STANDING_LABEL: Record<Standing, string> = {
  leading: "Leading",
  tied: "Tied",
  behind: "Behind",
  unknown: "No competitors tracked",
};

type Verdict = {
  level: "good" | "mixed" | "poor";
  icon: string;
  label: string;
  sentence: string;
  styles: string;
};

function computeVerdict(citationRate: number, standing: Standing): Verdict {
  if (citationRate >= 0.6 && standing !== "behind") {
    return {
      level: "good",
      icon: "✓",
      label: "Good outcome",
      sentence: "Your site is showing up well in AI search results.",
      styles: "border-cited/40 bg-cited/10 text-cited",
    };
  }
  if (citationRate >= 0.6 && standing === "behind") {
    return {
      level: "mixed",
      icon: "!",
      label: "Mixed signals",
      sentence: "You're showing up often, but a competitor is showing up even more — it's a close race.",
      styles: "border-accent/40 bg-accent/10 text-accent",
    };
  }
  if (citationRate >= 0.3) {
    return {
      level: "mixed",
      icon: "!",
      label: "Mixed signals",
      sentence: "Your site shows up sometimes, but a competitor is catching up.",
      styles: "border-accent/40 bg-accent/10 text-accent",
    };
  }
  return {
    level: "poor",
    icon: "✗",
    label: "Needs attention",
    sentence: "Your site is largely invisible to AI search assistants right now.",
    styles: "border-not-cited/40 bg-not-cited/10 text-not-cited",
  };
}

function standingSentence(standing: Standing): string {
  switch (standing) {
    case "leading":
      return "You're currently ahead of the competitors we checked — keep it that way.";
    case "tied":
      return "You're currently tied with a competitor — small improvements could put you clearly ahead.";
    case "behind":
      return "A competitor is currently showing up more often than you for the same questions.";
    default:
      return "We didn't have competitor data to compare against for this run.";
  }
}

export default function AtAGlance({
  citationRate,
  targetDomain,
  citationShare,
  totalQueries,
  citedQueries,
  topRoadmapTitle,
}: {
  citationRate: number;
  targetDomain: string;
  citationShare: Record<string, number> | null;
  totalQueries: number;
  citedQueries: number;
  topRoadmapTitle: string;
}) {
  const standing = computeStanding(citationShare, targetDomain);
  const verdict = computeVerdict(citationRate, standing);

  return (
    <section>
      <p className="text-xs font-medium uppercase tracking-wide text-muted">At a Glance</p>

      <div className={`mt-2 rounded border px-5 py-4 ${verdict.styles}`}>
        <p className="text-sm font-semibold">
          {verdict.icon} {verdict.label}: {verdict.sentence}
        </p>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        <StatCard label="How often AI mentions you" value={`${Math.round(citationRate * 100)}%`} />
        <StatCard label="vs. competitors" value={STANDING_LABEL[standing]} />
        <StatCard label="Most urgent fix" value={<LinkedText text={topRoadmapTitle} />} small />
      </div>

      <div className="mt-4 rounded border border-border bg-card px-5 py-4">
        <p className="text-xs font-medium uppercase tracking-wide text-muted">What This Means For You</p>
        <ul className="mt-2 list-inside list-disc space-y-1.5 text-sm">
          <li>
            Out of the {totalQueries} buyer question{totalQueries === 1 ? "" : "s"} we tested, AI mentioned{" "}
            <span className="font-mono">{targetDomain}</span> in {citedQueries}.
          </li>
          <li>{standingSentence(standing)}</li>
          <li>
            The single highest-impact fix right now: <LinkedText text={topRoadmapTitle} />.
          </li>
        </ul>
      </div>
    </section>
  );
}

function StatCard({ label, value, small }: { label: string; value: ReactNode; small?: boolean }) {
  return (
    <div className="rounded border border-border bg-card px-4 py-3">
      <p className="text-xs text-muted">{label}</p>
      <p className={`mt-1 font-semibold ${small ? "text-sm leading-snug" : "text-2xl"}`}>{value}</p>
    </div>
  );
}
