# GALXY · Module 5 - AI Preview Generation (m5_Frontend1)

This repository contains the front-end implementation for the customer-facing AI Preview Panel (`AIPreviewPanel`) on the custom product detail page, developed for the **Module 5 AI Preview Generation** feature branch (`feat-m5-frontend1-aipreviewpanel`).

---

## 📂 Project Structure

```
model/
├── assets/                     # Mock generated product and preview image assets
│   ├── neon_default.png        # Default base product image (unlit tubes)
│   ├── neon_blue.png           # Electric Blue neon glow preview
│   ├── neon_pink.png           # Neon Pink neon glow preview
│   └── neon_gold.png           # Warm Gold neon glow preview
│
├── src/                        # React Frontend Source
│   ├── components/
│   │   ├── AIPreviewPanel.jsx  # Production React component (m5_Frontend1 deliverable)
│   │   └── AIPreviewPanel.css  # Scoped component styling & scan-line animations
│   ├── App.jsx                 # Verification container wrapper for local testing
│   └── main.jsx                # React DOM mount entry-point
│
├── index.html                  # Interactive e-commerce configurator & API simulator (Standalone Demo)
├── index.css                   # General layout styles for the standalone demo
├── app.js                      # Mock server routing, log telemetry, and DOM logic for index.html
├── serve.ps1                   # Local Windows .NET HTTP server utility (Port 8080)
├── package.json                # Project dependencies (Vite + React)
├── vite.config.js              # Bundler configuration for React compiling
└── README.md                   # This instruction file
```

---

## ⚡ How to Run the Demos

### 1. The Configurator & API Simulator (HTML Prototype)
This runs in any browser and allows testing all required rate limit quotas, timeout states, cache logs, and stale states.

* **Option A: PowerShell Server (Windows)**:
  Run the provided script to start a lightweight native .NET server:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\serve.ps1
  ```
  Open `http://localhost:8080/` in your browser.

* **Option B: Cross-Platform Node Server**:
  ```bash
  npx serve ./
  ```

* **Option C: Python Server**:
  ```bash
  python -m http.server 8080
  ```

### 2. The Production React Component (Vite Setup)
To build or inspect the compilable React component:
1. Run `npm install` to install React and Vite dev dependencies.
2. Run `npm run dev` to start the local Vite server (Port 3000).
3. Run `npm run build` to compile the optimized production package under `/dist`.

---

## 🛡️ Completed Security & Feature Audits
* **Prompt Injection Defense**: Text customizer inputs are filtered through a client-side sanitization function which removes potential overrides (`ignore instructions`, `system prompt`, etc.) and restricts symbols to letters, numbers, and basic typography marks.
* **XSS Protection**: Simulator log console prints escaped HTML tags to prevent custom sign text from injecting executable scripts.
* **Strict Spec Order**: The API dispatch flow follows `Validate (400) -> Rate-Limit Check (429) -> Cache Check (served locally with zero quota consumption) -> API Request`.
* **Schema-Driven Heuristics**: Caching bypasses and attribute filters read the dynamic `affects_ai_preview` and `default_value` properties directly from Module 2's category attributes schema, avoiding hardcoded text/name rules.