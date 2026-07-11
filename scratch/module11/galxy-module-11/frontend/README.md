# GALXY — Notifications Hub Client

The user dashboard interface for managing notifications, account switching, order triggers, and Telegram notification alerts.

---

## 🛠️ Technology Stack
* **Language/Runtime**: Javascript / Node.js
* **Framework**: React 18
* **Build System**: Vite
* **Styling**: Tailwind CSS
* **Test Runner**: Vitest (jsdom environment)

---

## ⚙️ Setup & Execution

### 1. Installation
Navigate to the frontend folder and install all node modules:
```bash
cd frontend
npm install
```

### 2. Run the Web App
Start the Vite local development server:
```bash
npm run dev
```
*The React client will run on **`http://localhost:3050`**.*

> [!NOTE]
> Vite is configured to run on port `3050` to bypass cached browser service worker conflicts that occur when running on port `3000`.

---

## 🧪 Testing

To run the unit tests and component rendering tests:
```bash
npm run test
```

---

## 📡 API Integration Configuration

* **Connection Config**: Configured in [src/config.js](file:///c:/Users/sakth/OneDrive/Desktop/module%2011/frontend/src/config.js).
* **Base URL**: Defaults to `http://localhost:5000` (which connects to the local Flask backend).

### User Session Authentication
To mock user profiles (e.g. `customer1`, `customer2`) without database integration:
1. Select an account on the **Toggle User Account** control card.
2. The client fetches a mock signed JWT token from `/api/v1/auth/token` on the backend.
3. This token is saved to the browser's `localStorage` as `galxy_token` and automatically included in subsequent request headers.
