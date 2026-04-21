// Electron main process — creates a window, spawns the Python backend,
// loads the React build, and proxies /api to the local backend.

const { app, BrowserWindow, Menu, shell } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");

const BACKEND_PORT = 8765;
let mainWindow = null;
let pythonProcess = null;


function resolveRendererHtml() {
  // In dev, we expect the React dist in pypemesh-web/frontend/dist.
  const candidates = [
    path.join(__dirname, "renderer", "index.html"),
    path.join(__dirname, "..", "pypemesh-web", "frontend", "dist", "index.html"),
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}


function startPythonBackend() {
  // Try to launch `python -m uvicorn app.main:app` from the backend dir.
  const backendDir = path.join(__dirname, "..", "pypemesh-web", "backend");
  if (!fs.existsSync(backendDir)) {
    console.warn("backend dir not found at", backendDir, "— skipping Python launch");
    return;
  }
  try {
    pythonProcess = spawn(
      "python3",
      ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", String(BACKEND_PORT)],
      { cwd: backendDir, stdio: "inherit" },
    );
    pythonProcess.on("error", (err) => {
      console.warn("failed to start Python backend:", err.message);
    });
  } catch (e) {
    console.warn("failed to start Python backend:", e);
  }
}


function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill("SIGTERM");
    pythonProcess = null;
  }
}


function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: "pypemesh",
    backgroundColor: "#0b0d10",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
    },
  });

  const htmlPath = resolveRendererHtml();
  if (htmlPath) {
    mainWindow.loadFile(htmlPath);
  } else {
    // Fall back to the hosted Vercel site
    mainWindow.loadURL("https://pypemesh.vercel.app/");
  }

  // Open external links in the OS browser, not inside Electron
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}


app.whenReady().then(() => {
  startPythonBackend();
  createWindow();

  const template = [
    { role: "appMenu" },
    { role: "fileMenu" },
    { role: "editMenu" },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "toggleDevTools" },
        { type: "separator" },
        { role: "togglefullscreen" },
      ],
    },
    {
      label: "Help",
      submenu: [
        {
          label: "pypemesh on GitHub",
          click: () => shell.openExternal("https://github.com/mihirpatel231197-art/pypemesh"),
        },
        {
          label: "Documentation",
          click: () => shell.openExternal("https://mihirpatel231197-art.github.io/pypemesh/"),
        },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});


app.on("window-all-closed", () => {
  stopPythonBackend();
  if (process.platform !== "darwin") app.quit();
});


app.on("before-quit", () => stopPythonBackend());
