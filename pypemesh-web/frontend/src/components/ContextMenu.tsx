// Right-click context menu for 3D viewport — actions depend on what's under cursor.

import { useEffect } from "react";

export interface ContextMenuItem {
  label: string;
  shortcut?: string;
  disabled?: boolean;
  onClick?: () => void;
  divider?: boolean;
}

interface Props {
  x: number;
  y: number;
  items: ContextMenuItem[];
  onClose: () => void;
}

export function ContextMenu({ x, y, items, onClose }: Props) {
  useEffect(() => {
    function onDown(e: MouseEvent) {
      const el = e.target as HTMLElement;
      if (!el.closest(".context-menu")) onClose();
    }
    function onEsc(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onEsc);
    return () => {
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onEsc);
    };
  }, [onClose]);

  return (
    <div className="context-menu" style={{ left: x, top: y }}>
      {items.map((item, i) => item.divider ? (
        <div key={i} className="ctx-divider" />
      ) : (
        <button
          key={i}
          className="ctx-item"
          disabled={item.disabled}
          onClick={() => { item.onClick?.(); onClose(); }}
        >
          <span>{item.label}</span>
          {item.shortcut && <span className="ctx-shortcut">{item.shortcut}</span>}
        </button>
      ))}
    </div>
  );
}
