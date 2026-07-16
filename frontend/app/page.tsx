"use client";

import { useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type HealthStatus = "loading" | "ok" | "error";

export default function Home() {
  const [status, setStatus] = useState<HealthStatus>("loading");

  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`status ${res.status}`);
        return res.json();
      })
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-2xl font-semibold">AEO Product Ops System</h1>
      <p className="font-mono text-sm">
        Backend status:{" "}
        {status === "loading" && <span className="text-zinc-400">checking…</span>}
        {status === "ok" && <span className="text-green-500">✓ connected</span>}
        {status === "error" && <span className="text-red-500">✗ unreachable</span>}
      </p>
    </div>
  );
}
