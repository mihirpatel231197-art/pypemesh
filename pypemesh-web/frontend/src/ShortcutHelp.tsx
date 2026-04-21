import { useEffect } from "react";
import type { Shortcut } from "./useKeyboard";

interface Props {
  shortcuts: Shortcut[];
  open: boolean;
  onClose: () => void;
}

export function ShortcutHelp({ shortcuts, open, onClose }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="shortcut-overlay" onClick={onClose}>
      <div className="shortcut-card" onClick={(e) => e.stopPropagation()}>
        <h3>Keyboard shortcuts</h3>
        <table>
          <tbody>
            {shortcuts.map((s) => (
              <tr key={s.key}>
                <td><kbd>{s.key}</kbd></td>
                <td>{s.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="hint">Press <kbd>Esc</kbd> to close.</p>
      </div>
    </div>
  );
}
