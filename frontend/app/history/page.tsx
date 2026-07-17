import Link from "next/link";
import { listRuns } from "@/lib/api";

export default async function HistoryPage() {
  const runs = await listRuns().catch(() => []);

  return (
    <div>
      <h1 className="text-2xl font-semibold">History</h1>

      {runs.length === 0 ? (
        <div className="mt-8 text-center">
          <p className="text-sm text-muted">No audits run yet — start your first one</p>
          <Link
            href="/"
            className="mt-4 inline-block rounded bg-accent px-4 py-2 text-sm font-semibold text-white hover:opacity-90"
          >
            Run an audit
          </Link>
        </div>
      ) : (
        <div className="mt-6 overflow-x-auto rounded border border-border">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-card text-left text-xs uppercase tracking-wide text-muted">
                <th className="px-4 py-3 font-medium">Target URL</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} className="border-b border-border last:border-0">
                  <td className="px-4 py-3">
                    <Link href={`/report/${run.id}`} className="font-mono text-accent hover:underline">
                      {run.target_url}
                    </Link>
                  </td>
                  <td className="px-4 py-3">{run.status}</td>
                  <td className="px-4 py-3 text-muted">{new Date(run.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
