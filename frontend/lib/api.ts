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
