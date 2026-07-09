# GALXY — Module 6: Cart

This repository contains the completed **Cart UI Module (Module 6)** for the GALXY Custom Lighting & Craft Studio web application.

It is implemented as a modern React application utilizing Vite, styled with premium Tailwind CSS (v4) and custom glassmorphism overlays, and backed by a fully stateful, local-storage based API mocking layer that implements the standard API response envelopes.

---

## Technical Architecture

### 1. Data & State Layer
- **Mock DB & API Client (`src/api/mockCartApi.js`):** Replicates the required backend endpoints (`GET /api/cart`, `PUT /api/cart/items/:id`, `DELETE /api/cart/items/:id`, and `DELETE /api/cart/clear`). It performs precise price modifications based on active product attributes and base estimates without client-side recalculation assumptions.
- **Cart Context (`src/context/CartContext.jsx`):** Coordinates global cart state across navigation badge, quick-view drawer, and full cart page. Implements optimistic UI rendering, debounced API calls for the quantity stepper, and a global notification toast queue.

### 2. Presentational Components
- **`CartPage`:** The primary full cart view. Lists configured attributes, engravings, and custom request fields. Features a dynamic correctional modal that reads error details from the backend and guides users to resolve invalid choices (e.g. out-of-stock finishes).
- **`CartDrawer`:** A slide-out panel providing a quick summary of currently selected configurations and estimates.
- **`QuantityStepper`:** An interactive stepper that debounces inputs to avoid spamming the database.
- **`ControlPanel`:** A floating simulator dashboard in the bottom-left corner allowing developers to toggle item availability, trigger validation errors, and adjust API mock latency in real-time.

---

## Getting Started

### Installation
Install project dependencies:
```bash
npm install
```

### Run Locally
Start the development server:
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### Build Production Bundle
Compile and bundle the project:
```bash
npm run build
```

---

## Testing & QA Verification

Automated test cases are configured using the **Vitest** test runner.

To run the test suite:
```bash
npx vitest run
```

The tests cover:
- Core CRUD operations (`GET`, `PUT`, `DELETE`).
- Envelope structure contract verification.
- Unavailable items subtotal and `item_count` exclusions.
- Multi-click ID collision security.
