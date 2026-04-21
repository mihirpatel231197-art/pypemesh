// Undo/redo stack — infinite history, backed by a simple ref.
import { useCallback, useRef, useState } from "react";

export interface UndoableState<T> {
  state: T;
  push: (next: T) => void;
  undo: () => T | null;
  redo: () => T | null;
  canUndo: boolean;
  canRedo: boolean;
  reset: (state: T) => void;
  history: number;
}

/** Simple infinite undo/redo hook. Holds past + present + future. */
export function useUndo<T>(initial: T): UndoableState<T> {
  const [state, setState] = useState<T>(initial);
  const pastRef = useRef<T[]>([]);
  const futureRef = useRef<T[]>([]);
  const [version, setVersion] = useState(0);

  const push = useCallback((next: T) => {
    pastRef.current.push(state);
    futureRef.current = [];
    setState(next);
    setVersion((v) => v + 1);
  }, [state]);

  const undo = useCallback((): T | null => {
    const past = pastRef.current;
    if (past.length === 0) return null;
    const previous = past.pop()!;
    futureRef.current.push(state);
    setState(previous);
    setVersion((v) => v + 1);
    return previous;
  }, [state]);

  const redo = useCallback((): T | null => {
    const future = futureRef.current;
    if (future.length === 0) return null;
    const next = future.pop()!;
    pastRef.current.push(state);
    setState(next);
    setVersion((v) => v + 1);
    return next;
  }, [state]);

  const reset = useCallback((newState: T) => {
    pastRef.current = [];
    futureRef.current = [];
    setState(newState);
    setVersion((v) => v + 1);
  }, []);

  return {
    state,
    push,
    undo,
    redo,
    canUndo: pastRef.current.length > 0,
    canRedo: futureRef.current.length > 0,
    reset,
    history: version,
  };
}
