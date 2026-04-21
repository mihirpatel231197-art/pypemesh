// Preload script — expose a minimal safe API to the renderer if needed.
// Renderer runs with contextIsolation: true.

const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("pypemesh", {
  isDesktop: true,
  apiBase: "http://127.0.0.1:8765",
});
