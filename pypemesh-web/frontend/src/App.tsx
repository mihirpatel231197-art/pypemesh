export function App() {
  return (
    <div className="landing">
      <header>
        <div className="logo">pypemesh</div>
        <nav>
          <a href="https://github.com/pypemesh/pypemesh" aria-label="GitHub">
            GitHub
          </a>
          <a href="#roadmap">Roadmap</a>
        </nav>
      </header>

      <main>
        <section className="hero">
          <h1>
            The open-source pipe stress analysis platform.
          </h1>
          <p className="subtitle">
            Validated ASME B31.3 solver. CAD-like modeler. Cloud-first. MIT
            license. Built for engineers who want the power of Caesar II and
            the ergonomics of modern tools.
          </p>
          <div className="cta">
            <a className="btn-primary" href="#get-notified">Get notified at launch</a>
            <a className="btn-secondary" href="https://github.com/pypemesh/pypemesh">
              Star on GitHub
            </a>
          </div>
          <div className="status">
            <span className="dot" />
            Pre-alpha · Phase B in progress · See roadmap
          </div>
        </section>

        <section className="features">
          <div className="feature">
            <h3>Full code compliance</h3>
            <p>ASME B31.3 at launch. B31.1, B31.4, EN 13480 on the roadmap.</p>
          </div>
          <div className="feature">
            <h3>Modern 3D modeler</h3>
            <p>Point-and-click or Caesar-style spreadsheet. Both, always in sync.</p>
          </div>
          <div className="feature">
            <h3>Validated solver</h3>
            <p>Every release runs against published ASME, Markl, and textbook benchmarks.</p>
          </div>
          <div className="feature">
            <h3>Cloud-first</h3>
            <p>Collaborate in real time. Self-host if you prefer. Your data, your choice.</p>
          </div>
          <div className="feature">
            <h3>Open core</h3>
            <p>MIT-licensed. Audit it. Fork it. Build on it.</p>
          </div>
          <div className="feature">
            <h3>Plugin SDK</h3>
            <p>Codes, materials, CAD adapters as plugins. No vendor lock-in.</p>
          </div>
        </section>

        <section id="roadmap" className="roadmap">
          <h2>Roadmap</h2>
          <ol>
            <li><strong>Phase B</strong> · Open-source MVP · B31.3 static + dynamic · web modeler</li>
            <li><strong>Phase B.1</strong> · B31.1, B31.4, non-linear, PCF import</li>
            <li><strong>Phase B.2</strong> · AI support optimizer, local FEA, CAD plugins</li>
            <li><strong>Phase C</strong> · Commercial: nuclear, enterprise, licensed materials</li>
          </ol>
        </section>

        <footer>
          <p>MIT licensed · Not yet for safety-critical work · Always have a licensed PE review output.</p>
        </footer>
      </main>
    </div>
  );
}
