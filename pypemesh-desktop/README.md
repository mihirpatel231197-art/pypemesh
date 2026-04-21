# pypemesh-desktop

Electron wrapper for the pypemesh web app — ships as a native desktop
application for Windows, macOS, and Linux. Wraps the same React frontend
used by the Vercel deployment, plus bundles the FastAPI backend as a
child process.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Electron main process (main.js)                │
│   ├─ creates BrowserWindow                      │
│   ├─ spawns Python backend (uvicorn) on 8765    │
│   └─ loads file:///…/renderer/index.html        │
└─────────────────────────────────────────────────┘
                  ↕ same-origin HTTP
┌─────────────────────────────────────────────────┐
│  Renderer (React build from pypemesh-web/       │
│  frontend/dist) with VITE_API_BASE set to       │
│  http://127.0.0.1:8765                          │
└─────────────────────────────────────────────────┘
```

## Dev

```bash
# Build the frontend first (if not already built)
cd ../pypemesh-web/frontend && npm run build

# Install + run desktop
cd ../../pypemesh-desktop
npm install
npm start
```

## Package

```bash
npm run package         # all platforms via electron-builder
npm run package:mac     # macOS .dmg
npm run package:win     # Windows .exe
npm run package:linux   # Linux .AppImage / .deb
```

## Requirements

- Node 20+
- Python 3.11+ with `pypemesh-core` + `fastapi` + `uvicorn` installed on
  the user's system (or bundled via PyInstaller — future)

## Roadmap

- v0.2: bundle Python runtime via PyInstaller so end users don't need to
  install Python separately
- v0.3: auto-update via electron-updater
- v0.4: native menu integration, system tray, deep links
