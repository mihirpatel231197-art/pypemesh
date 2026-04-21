import { useState } from "react";
import { Modeler } from "./Modeler";
import { Sidebar } from "./Sidebar";
import { sampleProject } from "./sample";
import { solveProject } from "./api";
import type { SolveResponse } from "./types";

export function App() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [results, setResults] = useState<SolveResponse | null>(null);
  const [resultCombo, setResultCombo] = useState<string | null>(null);
  const [solving, setSolving] = useState(false);

  async function handleSolve() {
    setSolving(true);
    try {
      const res = await solveProject(sampleProject);
      setResults(res);
      // Default to first combination for coloring
      if (sampleProject.load_combinations.length > 0) {
        setResultCombo(sampleProject.load_combinations[0].id);
      }
    } finally {
      setSolving(false);
    }
  }

  return (
    <div className="app">
      <header>
        <div className="logo">pypemesh <span className="badge">pre-alpha</span></div>
        <nav>
          <a href="https://github.com/mihirpatel231197-art/pypemesh" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="#about">About</a>
        </nav>
      </header>

      <main>
        <section className="modeler-section">
          <div className="modeler-canvas">
            <Modeler
              project={sampleProject}
              selectedNode={selectedNode}
              selectedElement={selectedElement}
              onSelectNode={setSelectedNode}
              onSelectElement={setSelectedElement}
              results={results}
              resultCombo={resultCombo}
            />
          </div>
          <Sidebar
            project={sampleProject}
            selectedNode={selectedNode}
            selectedElement={selectedElement}
            onSelectNode={(id) => { setSelectedNode(id); setSelectedElement(null); }}
            onSelectElement={(id) => { setSelectedElement(id); setSelectedNode(null); }}
            results={results}
            resultCombo={resultCombo}
            onSelectCombo={setResultCombo}
            solving={solving}
            onSolve={handleSolve}
          />
        </section>

        <section id="about" className="about">
          <h2>What you're looking at</h2>
          <p>
            This is a live pypemesh model — a 5-node U-loop pipe (6&quot; SCH 40 carbon steel)
            with anchors at both ends, internal pressure of 50&nbsp;bar, and thermal expansion
            from 20&nbsp;°C to 120&nbsp;°C. Click <b>Run B31.3 check</b> to evaluate sustained
            and expansion stress per ASME B31.3 equations 23a and 17.
          </p>
          <p>
            The solver is a real 3D beam FEA written in Python (pypemesh-core, MIT license).
            All math derived from first principles in the <a href="https://github.com/mihirpatel231197-art/pypemesh/tree/main/docs/theory" target="_blank" rel="noreferrer">theory docs</a>.
            55 unit + analytical tests pass on every commit, including a benchmark validation harness.
          </p>
          <p className="note">
            If a backend is reachable at <code>VITE_API_BASE</code>, this calls
            <code>/solve</code> for live results. Otherwise it shows mock results so the
            demo still works.
          </p>
        </section>

        <section className="features">
          <div className="feature">
            <h3>Validated solver</h3>
            <p>Cantilever PL³/3EI to 0.1%. Thermal EAαΔT to 0.1%. B31.3 PD/4t exact.</p>
          </div>
          <div className="feature">
            <h3>Open core</h3>
            <p>MIT license. Audit it. Fork it. Extend it. No black boxes.</p>
          </div>
          <div className="feature">
            <h3>Modern stack</h3>
            <p>Python + SciPy + FastAPI + React + Three.js. Docker-deployable end-to-end.</p>
          </div>
          <div className="feature">
            <h3>Code coverage</h3>
            <p>ASME B31.3 today. B31.1, B31.4, EN 13480, nuclear on the roadmap.</p>
          </div>
        </section>

        <footer>
          <p>
            MIT licensed · Engineering analysis software requires PE review before use in
            safety-critical work. See <a href="https://github.com/mihirpatel231197-art/pypemesh/blob/main/LICENSE" target="_blank" rel="noreferrer">LICENSE</a>.
          </p>
        </footer>
      </main>
    </div>
  );
}
