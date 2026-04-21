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

export async function downloadReport(
  project: PipeProject,
  options: { company?: string; engineer?: string } = {},
): Promise<{ ok: boolean; message?: string }> {
  try {
    const res = await fetch(`${API_BASE}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project, ...options }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${project.project.name.replace(/\s+/g, "_")}_b31_3_report.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return { ok: true };
  } catch (err) {
    return {
      ok: false,
      message: "Backend not reachable — start the FastAPI backend locally to download a real PDF.",
    };
  }
}
