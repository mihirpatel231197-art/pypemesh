import type { ModesResponse, PipeProject, SolveResponse } from "./types";
import { mockResponse } from "./sample";

const mockModes: ModesResponse = {
  status: "ok",
  project_name: "U-loop demo (mock)",
  n_modes: 5,
  frequencies_hz: [12.4, 15.7, 28.1, 41.5, 62.8],
  angular_frequencies: [77.9, 98.6, 176.6, 260.7, 394.6],
  periods_s: [0.0807, 0.0637, 0.0356, 0.0241, 0.0159],
};

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://localhost:8000";

export async function solveProject(
  project: PipeProject,
  code: "B31.3" | "B31.1" | "B31.4" | "B31.8" | "EN-13480" = "B31.3",
): Promise<SolveResponse> {
  try {
    const res = await fetch(`${API_BASE}/solve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project, code }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return (await res.json()) as SolveResponse;
  } catch (err) {
    console.warn("Backend unreachable, using mock response:", err);
    await new Promise((r) => setTimeout(r, 600));
    return { ...mockResponse, code };
  }
}

export async function getModes(project: PipeProject, n_modes = 10): Promise<ModesResponse> {
  try {
    const res = await fetch(`${API_BASE}/modes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project, n_modes }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as ModesResponse;
  } catch (err) {
    console.warn("Backend unreachable, using mock modes:", err);
    await new Promise((r) => setTimeout(r, 400));
    return mockModes;
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
