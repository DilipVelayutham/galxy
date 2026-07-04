# GALXY — Module 5: AI Preview Generation Backend (Backend 1 - T1 + T2)

This directory contains the backend implementation of Module 5 (AI Preview Generation) for the GALXY Custom Lighting & Craft Studio platform. 

It implements **Backend 1 (T1 & T2)**: the core orchestration engine (`ai_service.py`), category prompt templating (`prompt_builder_service.py`), and the Gemini API client adapter (`ai_provider_client.py`), along with the POST API route and database/model configuration.

---

## 🛠️ Features Implemented (T1 + T2)

1. **Core Orchestration Engine (`app/services/ai_service.py`)**:
   - Executes the 7-step pipeline: Validation ➔ Rate Limit check ➔ Cache check ➔ Prompt assembly ➔ Gemini API call ➔ Cloudinary upload ➔ Log to MongoDB.
   - Delegates attribute validation to Module 4 (via `app/utils/module4_client.py`).
   - Checks rate-limits and caching (delegating to stubs in `ai_rate_limit_service.py` and `ai_cache_service.py` to be completed by Gokul/Backend 2).
   - Records all generations to MongoDB with timestamps, duration, prompts, and status.

2. **Prompt Builder (`app/services/prompt_builder_service.py`)**:
   - Parses placeholders matching category schema attributes.
   - Resolves option keys to human-readable labels (e.g. `cursive_v2` ➔ `Cursive`).
   - Excludes attributes flagged with `affects_ai_preview: false`.
   - Cleans up empty optional placeholder artifacts, punctuation, and extra spaces.
   - Sanitizes text inputs against prompt injection and malicious formatting.

3. **Gemini API Adapter (`app/services/ai_provider_client.py`)**:
   - Uses the `google-generativeai` SDK.
   - Enforces configurable timeout checks (`AI_GENERATION_TIMEOUT_SECONDS`).
   - Adapts to generic error responses (`ProviderError`, `ProviderTimeoutError`) so raw API secrets or stack traces never leak to the client.

4. **API Endpoints (`app/routes/ai_routes.py`)**:
   - `POST /api/ai/generate-preview` (Naveen/Backend 1)
   - `GET /api/ai/generations/:user_id` (Gokul/Backend 2 stub)

---

## ⚙️ Configuration & Setup

### 1. Environment Configuration
Create a `.env` file in the `backend/` directory (you can copy `.env.example` as a template):
```bash
cp .env.example .env
```
Update the variables to match your credentials:
```ini
MONGO_URI=mongodb://localhost:27017/galxy
GEMINI_API_KEY=your-gemini-api-key
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 2. Isolation / Development Mode
To develop/test in isolation without running the Module 4 server, set the following inside `.env`:
```ini
M4_VALIDATION_MODE=local
```
This enables a local fallback validator that simply checks if required attributes are present. Switch back to `http` when integrating.

---

## 🚀 Running the App

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Test Categories (Requires MongoDB running)
Seeds sample category definitions (`Neon Sign` and `LED Letter Sign`) equipped with `ai_prompt_template` configurations for preview generation:
```bash
python seed_categories.py
```

### 3. Run the Development Server
Starts the Flask server on port **5005**:
```bash
python run.py
```

---

## 🧪 Testing

The implementation is backed by a full test suite of **15 automated tests** covering prompt parsing logic, security sanitization, and API route responses (using fully mocked databases and API clients to run in isolation).

To run the tests:
```bash
python -m pytest
```
