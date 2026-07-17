export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Run = {
  id: string;
  target_url: string;
  competitor_urls: string[];
  buyer_queries: string[];
  status: "pending" | "running" | "complete" | "partial" | "failed";
  created_at: string;
  parent_run_id: string | null;
};

export type RoadmapItem = {
  id: string;
  run_id: string;
  title: string;
  reach: number;
  impact: number;
  confidence: number;
  effort: number;
  rice_score: number;
  description: string;
  status: string;
};

export type Prd = {
  title: string;
  problem_statement: string;
  proposed_solution: string;
  success_metric: string;
  scope_in: string[];
  scope_out: string[];
};

export type ParentRoadmapItem = {
  id: string;
  title: string;
  status: string;
};

export type Comparison = {
  parent_run_id: string;
  citation_rate_before: number;
  citation_rate_after: number;
  parent_roadmap: ParentRoadmapItem[];
};

export type Report = {
  roadmap: RoadmapItem[];
  prd: Prd;
  stakeholder_summary: string;
  comparison: Comparison | null;
};

export type TechnicalSeoIssue = {
  severity: "high" | "medium" | "low";
  issue: string;
  recommendation: string;
};

export type TechnicalSeoOutput = {
  summary: string;
  score: number;
  issues: TechnicalSeoIssue[];
  raw_findings: {
    url: string;
    json_ld_present: boolean;
    json_ld_types: string[];
    title: string | null;
    meta_description: string | null;
    h1_count: number;
    h2_count: number;
  };
};

export type AeoSignalCompetitor = {
  url: string;
  cited: boolean;
  reasoning: string;
};

export type AeoSignalQueryResult = {
  query: string;
  target_cited: boolean;
  target_reasoning: string;
  competitors: AeoSignalCompetitor[];
};

export type AeoSignalOutput = {
  target_domain: string;
  citation_rate: number;
  summary: string;
  query_results: AeoSignalQueryResult[];
};

export type ContentStrategyRecommendation = {
  recommendation: string;
  based_on: string;
};

export type ContentStrategyOutput = {
  summary: string;
  recommendations: ContentStrategyRecommendation[];
};

export type CompetitiveIntelLosingQuery = {
  query: string;
  winning_competitors: string[];
};

export type CompetitiveIntelOutput = {
  citation_share: Record<string, number>;
  queries_losing: CompetitiveIntelLosingQuery[];
  narrative: string;
};

export type AgentFinding<T> = { status: "success" | "error"; raw_output: T | { error: string } } | null;

export type AgentFindings = {
  technical_seo: AgentFinding<TechnicalSeoOutput>;
  aeo_signal: AgentFinding<AeoSignalOutput>;
  content_strategy: AgentFinding<ContentStrategyOutput>;
  competitive_intel: AgentFinding<CompetitiveIntelOutput>;
};

export type PipelineStep = {
  agent: string;
  status: "success" | "error";
};

export type PipelineResult = {
  run_id: string;
  status: Run["status"];
  steps: PipelineStep[];
  synthesizer_output: Report | null;
};

async function extractErrorMessage(res: Response): Promise<string> {
  try {
    const body = await res.json();
    // FastAPI validation errors: {"detail": [{"msg": "...", "loc": [...]}, ...]}
    if (Array.isArray(body?.detail)) {
      return body.detail
        .map((e: { msg?: string }) => e.msg?.replace(/^Value error,\s*/, "") ?? JSON.stringify(e))
        .join("; ");
    }
    // Plain HTTPException errors: {"detail": "..."}
    if (typeof body?.detail === "string") {
      return body.detail;
    }
  } catch {
    // response wasn't JSON — fall through to the generic message below
  }
  return `Request failed with status ${res.status}`;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res));
  }
  return res.json();
}

export function createRun(input: {
  target_url: string;
  competitor_urls: string[];
  buyer_queries: string[];
}): Promise<Run> {
  return apiFetch<Run>("/runs", { method: "POST", body: JSON.stringify(input) });
}

export function runFullPipeline(runId: string): Promise<PipelineResult> {
  return apiFetch<PipelineResult>(`/runs/${runId}/run-full-pipeline`, { method: "POST" });
}

export function getRun(runId: string): Promise<Run> {
  return apiFetch<Run>(`/runs/${runId}`);
}

export function listRuns(): Promise<Run[]> {
  return apiFetch<Run[]>("/runs");
}

export function getRoadmap(runId: string): Promise<RoadmapItem[]> {
  return apiFetch<RoadmapItem[]>(`/runs/${runId}/roadmap`);
}

export function getReport(runId: string): Promise<Report> {
  return apiFetch<Report>(`/runs/${runId}/report`);
}

export function rerun(runId: string): Promise<Run> {
  return apiFetch<Run>(`/runs/${runId}/rerun`, { method: "POST" });
}

export function getAgentFindings(runId: string): Promise<AgentFindings> {
  return apiFetch<AgentFindings>(`/runs/${runId}/agent-findings`);
}
