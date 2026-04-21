import type { PipeProject, SolveResponse } from "./types";
import { mockResponse } from "./sample";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://localhost:8000";

export async function solveProject(project: PipeProject): Promise<SolveResponse> {
  try {
    const res = await fetch(`${API_BASE}/solve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project, code: "B31.3" }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return (await res.json()) as SolveResponse;
  } catch (err) {
    console.warn("Backend unreachable, using mock response:", err);
    await new Promise((r) => setTimeout(r, 600)); // mimic latency
    return mockResponse;
  }
}
