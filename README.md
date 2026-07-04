# GALXY · Module 5 - AI Preview Generation (m5_Frontend1)

This repository contains the front-end implementation for the customer-facing AI Preview Panel (`AIPreviewPanel`) on the custom product detail page, developed for the **Module 5 AI Preview Generation** feature branch (`feat-m5-frontend1-aipreviewpanel`).

---

## 📂 Project Structure

```
./ (Repository Root)
├── assets/                     # Consolidated mock generated assets
│   ├── neon_default.png        # Default base product image (unlit tubes)
│   ├── neon_blue.png           # Electric Blue neon glow preview
│   ├── neon_pink.png           # Neon Pink neon glow preview
│   └── neon_gold.png           # Warm Gold neon glow preview
│
├── demo/                       # Standalone HTML/JS e-commerce prototype & simulator
│   ├── index.html              # Custom sign configurator simulator dashboard
│   ├── index.css               # Styling rules for layout, neon frames, and timers
│   ├── app.js                  # Mock server routing, cache logs, and quota logic
│   └── serve.ps1               # Lightweight Windows .NET HTTP server launcher (Port 8080)
│
├── src/                        # Production React Frontend Source
│   ├── components/
│   │   ├── AIPreviewPanel.jsx  # Production React component (m5_Frontend1 deliverable)
│   │   └── AIPreviewPanel.css  # Scoped component styling & scan-line animations
│   ├── App.jsx                 # Verification container wrapper for local testing
│   └── main.jsx                # React DOM mount entry-point
│
├── index.html                  # Vite root entry-point (binds to src/main.jsx)
├── package.json                # Project dependencies (Vite + React)
├── vite.config.js              # Bundler configuration for React compiling
└── README.md                   # This instruction file
```

---

## ⚡ How to Run the Demos

### 1. The Production React Component (Vite Setup)
To build or run the interactive React component:
1. Run `npm install` to install React and Vite dev dependencies.
2. Run `npm run dev` to start the local Vite server (Port 3000). The server maps to the root `index.html` which mounts the React `App` tree directly.
3. Run `npm run build` to compile the optimized production package under `/dist`.

### 2. The Standalone Configurator & API Simulator
This runs in any browser and allows simulating API response conditions (quota exhaustion 429, validations 400, gateway timeouts 504, provider faults 502).

* **Option A: PowerShell Server (Windows)**:
  Run the script inside the `/demo` folder:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\demo\serve.ps1
  ```
  Open `http://localhost:8080/` in your browser.

* **Option B: Cross-Platform Node Server**:
  ```bash
  npx serve ./demo
  ```

* **Option C: Python Server**:
  ```bash
  python -m http.server 8080 --directory ./demo
  ```

---

## 🛡️ Completed Security & Feature Audits
* **Vite Entry Point**: Relocated root HTML assets into `/demo/` and configured the root `index.html` to target the React virtual DOM. This allows bundler utilities to compile the component code directly.
* **Loading State Animation**: Removed circular spinner visuals to conform to styling rules. The loading panel only displays custom glowing gradient lines.
* **Handoff ID Tracking**: Exposed `generation_id` strings (as a small metadata badge next to the cache status) inside both the React component and the HTML prototype to allow easy verification for downstream integrations (e.g., `AIGenerationHistory`).
* **Prompt Injection Defense**: Text customizer inputs are filtered through a client-side sanitization function which removes potential overrides (`ignore instructions`, `system prompt`, etc.) and restricts symbols. Note: This client-side check is a user experience layer and should complement server-side prompt sanitization.
* **XSS Protection**: Log telemetries escape raw HTML characters.
* **Strict Spec Order**: The API dispatch flow follows `Validate (400) -> Rate-Limit Check (429) -> Cache Check (served locally) -> API Request`.
* **Schema-Driven Heuristics**: Caching bypasses and attribute filters read the dynamic `affects_ai_preview` and `default_value` properties directly from Module 2's category attributes schema, avoiding hardcoded text/name rules.