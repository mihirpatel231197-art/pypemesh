// localStorage autosave — persists project state every 30s.
import { useEffect, useRef } from "react";

const AUTOSAVE_KEY = "pypemesh.autosave.v1";
const AUTOSAVE_INTERVAL_MS = 30_000;


export function loadAutosaved<T>(): T | null {
  try {
    const raw = localStorage.getItem(AUTOSAVE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}


export function clearAutosave(): void {
  try { localStorage.removeItem(AUTOSAVE_KEY); } catch {}
}


export function useAutosave<T>(data: T, enabled: boolean = true) {
  const lastSavedRef = useRef<string>("");

  useEffect(() => {
    if (!enabled) return;
    function save() {
      try {
        const serialized = JSON.stringify(data);
        if (serialized !== lastSavedRef.current) {
          localStorage.setItem(AUTOSAVE_KEY, serialized);
          lastSavedRef.current = serialized;
        }
      } catch (e) {
        console.warn("autosave failed:", e);
      }
    }
    save();  // initial
    const id = setInterval(save, AUTOSAVE_INTERVAL_MS);
    const onBeforeUnload = () => save();
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => {
      clearInterval(id);
      window.removeEventListener("beforeunload", onBeforeUnload);
    };
  }, [data, enabled]);
}
