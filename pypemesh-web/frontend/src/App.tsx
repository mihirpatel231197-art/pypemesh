import { useEffect, useState } from "react";
import { DesignViewport } from "./components/DesignViewport";
import { Modeler } from "./Modeler";
import { Toolbar } from "./components/Toolbar";
import { PropertyEditor } from "./components/PropertyEditor";
import { LibraryBrowser } from "./components/LibraryBrowser";
import { LoadCaseEditor } from "./components/LoadCaseEditor";
import { ImportExportBar } from "./components/ImportExportBar";
import { ShortcutHelp } from "./ShortcutHelp";
import { SAMPLE_PROJECTS } from "./sample";
import { solveProject } from "./api";
import { useKeyboardShortcuts } from "./useKeyboard";
import { useProjectStore } from "./store/projectStore";
import type { ModeShape, SolveResponse } from "./types";

type CodeChoice =
  | "B31.3" | "B31.1" | "B31.4" | "B31.5"
  | "B31.8" | "B31.9" | "B31.12"
  | "CSA-Z662" | "DNV-ST-F101" | "EN-13480";

export function App() {
  const project = useProjectStore((s) => s.project);
  const setProject = useProjectStore((s) => s.setProject);
  const mode = useProjectStore((s) => s.mode);
  const setMode = useProjectStore((s) => s.setMode);
  const undo = useProjectStore((s) => s.undo);
  const redo = useProjectStore((s) => s.redo);
  const clearSelection = useProjectStore((s) => s.clearSelection);
  const setTool = useProjectStore((s) => s.setTool);

  const [selectedCode, setSelectedCode] = useState<CodeChoice>("B31.3");
  const [results, setResults] = useState<SolveResponse | null>(null);
  const [resultCombo, setResultCombo] = useState<string | null>(null);
  const [solving, setSolving] = useState(false);
  const [modesData] = useState<ModeShape[] | null>(null);
  const [animatedModeIndex] = useState<number | null>(null);
  const [shortcutHelpOpen, setShortcutHelpOpen] = useState(false);
  const [samplePicker, setSamplePicker] = useState<string>("u-loop");

  useEffect(() => {
    if (project.nodes.length === 0) {
      setProject(SAMPLE_PROJECTS[0].project);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function loadSample(id: string) {
    setSamplePicker(id);
    if (id === "__blank__") {
      setProject({
        schema_version: "0.1.0",
        project: { name: "Untitled" },
        nodes: [], elements: [], sections: [], materials: [], restraints: [],
        load_cases: [{ id: "W", kind: "weight" }],
        load_combinations: [{ id: "SUS", cases: ["W"], category: "sustained" }],
        code: "B31.3", code_version: "2022",
      });
    } else {
      const sample = SAMPLE_PROJECTS.find((s) => s.id === id);
      if (sample) setProject(sample.project);
    }
    setResults(null);
  }

  async function handleSolve() {
    setSolving(true);
    try {
      const res = await solveProject(project, selectedCode);
      setResults(res);
      if (project.load_combinations.length > 0) {
        setResultCombo(project.load_combinations[0].id);
      }
      setMode("analysis");
    } finally {
      setSolving(false);
    }
  }

  const animatedMode = (modesData && animatedModeIndex !== null)
    ? modesData[animatedModeIndex] ?? null
    : null;

  const shortcuts = [
    { key: "?", description: "Show shortcut help", handler: () => setShortcutHelpOpen(true) },
    { key: "r", description: "Run code check", handler: () => handleSolve() },
    { key: "cmd+z", description: "Undo", handler: () => undo() },
    { key: "cmd+shift+z", description: "Redo", handler: () => redo() },
    { key: "escape", description: "Clear selection / tool",
      handler: () => { clearSelection(); setTool("select"); setShortcutHelpOpen(false); } },
    { key: "s", description: "Select tool", handler: () => setTool("select") },
    { key: "n", description: "Add-node tool", handler: () => setTool("add-node") },
    { key: "p", description: "Connect-pipe tool", handler: () => setTool("connect-pipe") },
    { key: "e", description: "Connect-elbow tool", handler: () => setTool("connect-elbow") },
    { key: "a", description: "Anchor tool", handler: () => setTool("add-restraint") },
    { key: "d", description: "Delete tool", handler: () => setTool("delete") },
    { key: "m", description: "Toggle Design / Analyze",
      handler: () => setMode(mode === "design" ? "analysis" : "design") },
  ];
  useKeyboardShortcuts(shortcuts);

  return (
    <div className="app cad">
      <ShortcutHelp shortcuts={shortcuts} open={shortcutHelpOpen} onClose={() => setShortcutHelpOpen(false)} />
      <header className="cad-header">
        <div className="logo">pypemesh <span className="badge">pre-alpha</span></div>
        <div className="header-middle">
          <select
            className="sample-select"
            value={samplePicker}
            onChange={(e) => loadSample(e.target.value)}
          >
            <option value="__blank__">＋ Blank project</option>
            {SAMPLE_PROJECTS.map((s) => (
              <option key={s.id} value={s.id}>📁 {s.label}</option>
            ))}
          </select>
          <ImportExportBar />
        </div>
        <nav>
          <a href="#" onClick={(e) => { e.preventDefault(); setShortcutHelpOpen(true); }}>?</a>
          <a href="https://github.com/mihirpatel231197-art/pypemesh" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="https://mihirpatel231197-art.github.io/pypemesh/" target="_blank" rel="noreferrer">
            Docs
          </a>
        </nav>
      </header>

      <Toolbar />

      <div className="cad-layout">
        <aside className="cad-left">
          <LibraryBrowser />
        </aside>

        <main className="cad-main">
          {mode === "design" ? (
            <DesignViewport />
          ) : (
            <Modeler
              project={project}
              selectedNode={null}
              selectedElement={null}
              onSelectNode={() => {}}
              onSelectElement={() => {}}
              results={results}
              resultCombo={resultCombo}
              animatedMode={animatedMode}
              animationSpeed={1.5}
              animationAmplitude={0.4}
            />
          )}
        </main>

        <aside className="cad-right">
          <section className="panel">
            <h3>Properties</h3>
            <PropertyEditor />
          </section>

          <section className="panel">
            <h3>Loads</h3>
            <LoadCaseEditor />
          </section>

          <section className="panel panel-analysis">
            <h3>Analysis</h3>
            <div className="analysis-config">
              <label>Code</label>
              <select
                value={selectedCode}
                onChange={(e) => setSelectedCode(e.target.value as CodeChoice)}
              >
                <option value="B31.3">ASME B31.3 (process)</option>
                <option value="B31.1">ASME B31.1 (power)</option>
                <option value="B31.4">ASME B31.4 (liquid pipeline)</option>
                <option value="B31.5">ASME B31.5 (refrigeration)</option>
                <option value="B31.8">ASME B31.8 (gas transmission)</option>
                <option value="B31.9">ASME B31.9 (building services)</option>
                <option value="B31.12">ASME B31.12 (hydrogen)</option>
                <option value="CSA-Z662">CSA Z662 (Canadian)</option>
                <option value="DNV-ST-F101">DNV-ST-F101 (offshore)</option>
                <option value="EN-13480">EN 13480 (European)</option>
              </select>
            </div>
            <button
              className="btn-primary-big"
              onClick={handleSolve}
              disabled={solving || project.elements.length === 0}
            >
              {solving ? "Solving…" : "▶ Run analysis"}
            </button>
            {results && (
              <div className="results-summary">
                <div className={`status-pill ${results.summary.overall_status}`}>
                  {results.summary.overall_status.toUpperCase()}
                </div>
                <div className="kv"><span>Checks</span><b>{results.summary.total_checks}</b></div>
                <div className="kv"><span>Failed</span><b>{results.summary.failed}</b></div>
                <div className="kv"><span>Max ratio</span><b>{(results.summary.max_ratio * 100).toFixed(1)}%</b></div>
                <div className="combo-select">
                  {project.load_combinations.map((c) => (
                    <button
                      key={c.id}
                      className={`combo-btn ${resultCombo === c.id ? "active" : ""}`}
                      onClick={() => setResultCombo(c.id)}
                    >
                      {c.id}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}
