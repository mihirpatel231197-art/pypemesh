// Combined left panel — Library browser + Feature tree tabs.

import { useState } from "react";
import { LibraryBrowser } from "./LibraryBrowser";
import { FeatureTree } from "./FeatureTree";

export function LeftPanel() {
  const [tab, setTab] = useState<"library" | "tree">("library");

  return (
    <div className="left-panel">
      <div className="left-panel-tabs">
        <button
          className={`lp-tab ${tab === "library" ? "active" : ""}`}
          onClick={() => setTab("library")}
        >
          Library
        </button>
        <button
          className={`lp-tab ${tab === "tree" ? "active" : ""}`}
          onClick={() => setTab("tree")}
        >
          Tree
        </button>
      </div>
      <div className="left-panel-body">
        {tab === "library" ? <LibraryBrowser /> : <FeatureTree />}
      </div>
    </div>
  );
}
