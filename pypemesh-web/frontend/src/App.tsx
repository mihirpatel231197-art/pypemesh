import { useState } from "react";
import { Modeler } from "./Modeler";
import { Sidebar } from "./Sidebar";
import { SAMPLE_PROJECTS } from "./sample";
import { solveProject } from "./api";
import type { ModeShape, SolveResponse } from "./types";

type CodeChoice =
  | "B31.3" | "B31.1" | "B31.4" | "B31.5"
  | "B31.8" | "B31.9" | "B31.12"
  | "CSA-Z662" | "EN-13480";

export function App() {
  const [selectedSample, setSelectedSample] = useState<string>(SAMPLE_PROJECTS[0].id);
  const [selectedCode, setSelectedCode] = useState<CodeChoice>("B31.3");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [results, setResults] = useState<SolveResponse | null>(null);
  const [resultCombo, setResultCombo] = useState<string | null>(null);
  const [solving, setSolving] = useState(false);
  const [modesData, setModesData] = useState<ModeShape[] | null>(null);
  const [animatedModeIndex, setAnimatedModeIndex] = useState<number | null>(null);

  const project = SAMPLE_PROJECTS.find((s) => s.id === selectedSample)!.project;

  function handleSelectSample(id: string) {
    setSelectedSample(id);
    setSelectedNode(null);
    setSelectedElement(null);
    setResults(null);
    setResultCombo(null);
    setModesData(null);
    setAnimatedModeIndex(null);
  }

  async function handleSolve() {
    setSolving(true);
    try {
      const res = await solveProject(project, selectedCode);
      setResults(res);
      if (project.load_combinations.length > 0) {
        setResultCombo(project.load_combinations[0].id);
      }
    } finally {
      setSolving(false);
    }
  }

  const animatedMode = (modesData && animatedModeIndex !== null)
    ? modesData[animatedModeIndex] ?? null
    : null;

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
            <div className="sample-picker">
              <label>Sample:</label>
              <select value={selectedSample} onChange={(e) => handleSelectSample(e.target.value)}>
                {SAMPLE_PROJECTS.map((s) => (
                  <option key={s.id} value={s.id}>{s.label}</option>
                ))}
              </select>
              <label>Code:</label>
              <select value={selectedCode} onChange={(e) => setSelectedCode(e.target.value as CodeChoice)}>
                <option value="B31.3">ASME B31.3 (process)</option>
                <option value="B31.1">ASME B31.1 (power)</option>
                <option value="B31.4">ASME B31.4 (liquid pipeline)</option>
                <option value="B31.5">ASME B31.5 (refrigeration)</option>
                <option value="B31.8">ASME B31.8 (gas transmission)</option>
                <option value="B31.9">ASME B31.9 (building services)</option>
                <option value="B31.12">ASME B31.12 (hydrogen)</option>
                <option value="CSA-Z662">CSA Z662 (Canadian pipeline)</option>
                <option value="EN-13480">EN 13480 (European)</option>
              </select>
              {animatedMode && (
                <div className="anim-badge">
                  ▶ Mode {animatedMode.mode_index + 1} · {animatedMode.frequency_hz.toFixed(2)} Hz
                </div>
              )}
            </div>
            <Modeler
              project={project}
              selectedNode={selectedNode}
              selectedElement={selectedElement}
              onSelectNode={setSelectedNode}
              onSelectElement={setSelectedElement}
              results={results}
              resultCombo={resultCombo}
              animatedMode={animatedMode}
              animationSpeed={1.5}
              animationAmplitude={0.4}
            />
          </div>
          <Sidebar
            project={project}
            selectedNode={selectedNode}
            selectedElement={selectedElement}
            onSelectNode={(id) => { setSelectedNode(id); setSelectedElement(null); }}
            onSelectElement={(id) => { setSelectedElement(id); setSelectedNode(null); }}
            results={results}
            resultCombo={resultCombo}
            onSelectCombo={setResultCombo}
            solving={solving}
            onSolve={handleSolve}
            animatedModeIndex={animatedModeIndex}
            onSelectAnimatedMode={setAnimatedModeIndex}
            onModesLoaded={setModesData}
          />
        </section>

        <section id="about" className="about">
          <h2>What you're looking at</h2>
          <p>
            Live pypemesh demo — pick from 5 piping models, choose ASME B31.3 (process),
            B31.1 (power), or B31.4 (liquid pipeline), then click <b>Run code check</b>
            for color-coded stress overlays. Click <b>Compute first 5 natural frequencies</b>
            then click any mode to see it animate in 3D.
          </p>
          <p>
            The solver is a real 3D beam FEA written in Python (pypemesh-core, MIT license).
            All math derived from first principles in the <a href="https://github.com/mihirpatel231197-art/pypemesh/tree/main/docs/theory" target="_blank" rel="noreferrer">theory docs</a>.
            111+ unit and analytical tests pass on every commit. Validated to &lt;0.1% on
            cantilever / thermal / modal benchmarks.
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
            <p>Cantilever PL³/3EI &lt;0.1%. Thermal EAαΔT &lt;0.1%. Modal first mode &lt;0.02%.</p>
          </div>
          <div className="feature">
            <h3>3 codes shipping</h3>
            <p>B31.3 process, B31.1 power, B31.4 pipeline. EN 13480 + nuclear on roadmap.</p>
          </div>
          <div className="feature">
            <h3>Full dynamics</h3>
            <p>Modal + response spectrum (SRSS/CQC) + time history (Newmark-β).</p>
          </div>
          <div className="feature">
            <h3>Open core</h3>
            <p>MIT license. PCF file import. CLI tool. FastAPI backend. Audit it all.</p>
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
