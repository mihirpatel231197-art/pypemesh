// Bottom command-line bar — AutoCAD/SolidWorks style.
// Type a command to create/select/measure/dim. `help` shows the list.

import { useEffect, useRef, useState } from "react";
import { useProjectStore } from "../store/projectStore";

interface HistoryEntry {
  cmd: string;
  ok: boolean;
  message: string;
}

export function CommandLine() {
  const runCommand = useProjectStore((s) => s.runCommand);
  const [value, setValue] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      // Focus command line on "/" (GitHub-style) or ":"
      if ((e.key === "/" || e.key === ":") && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  function submit() {
    const cmd = value.trim();
    if (!cmd) return;
    const r = runCommand(cmd);
    setHistory((h) => [...h, { cmd, ok: r.ok, message: r.message }].slice(-50));
    setValue("");
    setHistoryIndex(-1);
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") { e.preventDefault(); submit(); }
    else if (e.key === "ArrowUp") {
      e.preventDefault();
      const cmds = history.map((h) => h.cmd);
      const idx = historyIndex < 0 ? cmds.length - 1 : Math.max(0, historyIndex - 1);
      if (cmds.length > 0) { setHistoryIndex(idx); setValue(cmds[idx]); }
    }
    else if (e.key === "ArrowDown") {
      e.preventDefault();
      const cmds = history.map((h) => h.cmd);
      if (historyIndex < 0) return;
      const idx = Math.min(cmds.length - 1, historyIndex + 1);
      setHistoryIndex(idx);
      setValue(cmds[idx] ?? "");
    }
    else if (e.key === "Escape") {
      setValue("");
      inputRef.current?.blur();
    }
  }

  const lastEntry = history[history.length - 1];

  return (
    <div className="command-line">
      <div className="cmd-prompt">
        <span className="cmd-caret">›</span>
        <input
          ref={inputRef}
          type="text"
          value={value}
          placeholder="type `help` for commands (e.g. node 0 0 0 · pipe N10 N20 · anchor N10 · extrude +X 3.0)"
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          spellCheck={false}
          autoCorrect="off"
          autoCapitalize="off"
        />
      </div>
      {lastEntry && (
        <div className={`cmd-status ${lastEntry.ok ? "ok" : "err"}`}>
          <span className="cmd-status-cmd mono">{lastEntry.cmd}</span>
          <span>→</span>
          <span>{lastEntry.message}</span>
        </div>
      )}
    </div>
  );
}
