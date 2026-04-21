// Keyboard shortcut registry with a searchable help overlay.
import { useEffect } from "react";

export interface Shortcut {
  key: string;           // e.g. "cmd+z", "ctrl+k", "?"
  description: string;
  handler: () => void;
}

function matchesShortcut(e: KeyboardEvent, key: string): boolean {
  const parts = key.toLowerCase().split("+").map((p) => p.trim());
  const needsCtrl = parts.includes("ctrl") || parts.includes("cmd");
  const needsShift = parts.includes("shift");
  const needsAlt = parts.includes("alt") || parts.includes("option");
  const letter = parts[parts.length - 1];

  // Match Cmd (macOS) or Ctrl (other) depending on what's available
  const ctrlOk = !needsCtrl || e.metaKey || e.ctrlKey;
  const shiftOk = needsShift === e.shiftKey;
  const altOk = needsAlt === e.altKey;
  const keyOk = e.key.toLowerCase() === letter;

  return ctrlOk && shiftOk && altOk && keyOk;
}

export function useKeyboardShortcuts(shortcuts: Shortcut[]) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      for (const s of shortcuts) {
        if (matchesShortcut(e, s.key)) {
          e.preventDefault();
          s.handler();
          return;
        }
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [shortcuts]);
}
