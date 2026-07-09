# GALXY CMS & Site Content Consolidated Module (Module 10)

This is the consolidated codebase for **Module 10 (Site Content / CMS & Shared Media Uploads)** of the GALXY Custom Lighting & Craft Studio application. It combines Next.js frontend forms, public UI pages, and the Flask Python backend with Cloudinary media uploading support.

---

## 1. Project Directory Structure
```text
galxy-module-10-merged/
 ├── app/
 │    ├── (admin)/                   # Next.js admin CMS pages
 │    ├── (public)/                  # Next.js public pages
 │    ├── models/
 │    │    └── site_content.py       # MongoDB collection registrations
 │    ├── routes/
 │    │    ├── site_content_routes.py # Public API endpoints (single & bulk GET)
 │    │    ├── admin_site_content_routes.py # Admin CMS management API endpoints
 │    │    └── media_routes.py       # Shared Cloudinary media upload routes
 │    ├── services/
 │    │    ├── site_content_service.py # CRUD operations for database
 │    │    └── media_upload_service.py # Core Cloudinary upload logic with retries
 │    ├── utils/
 │    │    ├── cloudinary_helper.py  # Cloudinary SDK wrapper
 │    │    ├── content_schema_validator.py # Strict schemas and validations
 │    │    ├── exceptions.py         # Custom media upload exceptions
 │    │    └── _dev_auth_stub.py     # Standalone auth token verification
 │    ├── middleware/
 │    │    └── auth.py               # Auth wrapper for media upload routes
 │    ├── config/
 │    │    └── config.py             # Config wrapper for media upload routes
 │    ├── globals.css                # Global Next.js styles
 │    ├── layout.tsx                 # Root layout file
 │    └── __init__.py                # Flask application factory
 ├── components/
 │    ├── admin/                     # Admin CMS form UI components
 │    └── site-content/              # Public home, about, contact UI components
 ├── lib/
 │    ├── api/                       # API request clients
 │    └── types/
 │         └── site-content.ts       # Unified typescript interfaces matching schema
 ├── public/                         # Public frontend assets (fonts, icons)
 ├── scripts/
 │    └── seed_site_content.py       # Idempotent defaults database seeder
 ├── tests/
 │    ├── conftest.py                # Pytest fixtures and configurations
 │    ├── test_site_content.py       # Test suite for CMS endpoints (13 tests)
 │    └── test_media_upload.py       # Test suite for media uploading (15 tests)
 ├── .env.example                    # Unified environment template keys
 ├── .gitignore                      # Git ignore file
 ├── config.py                       # Main Flask settings configuration loader
 ├── run.py                          # Flask entry point
 ├── requirements.txt                # Python dependencies list
 ├── tsconfig.json                   # Typescript configuration file
 ├── package.json                    # Frontend node dependencies
 └── package-lock.json               # Frontend package lock file
```

---

## 2. Environment Setup & Configuration

Create a `.env` file in the root folder. The following keys are required:

```ini
# Flask Backend Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_RUN_PORT=5000
SECRET_KEY=your_flask_secret_key_here

# MongoDB Configuration
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-address>/?appName=galxy-cluster
MONGO_DB_NAME=galxy

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# JWT Secret (from Module 1 for admin verification)
JWT_SECRET=your_jwt_secret_key_here

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Next.js Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## 3. Backend Setup & Run

### A. Installing Python Dependencies
Initialize a virtual environment and install the required dependencies:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
pip install certifi
```

### B. Database Seeding (Critical First Step)
To ensure database collection schemas and default data exist before running the frontend, run the seeder script:
```powershell
python scripts/seed_site_content.py
```

### C. Running the Flask Server
Start the local server on `http://127.0.0.1:5000/`:
```powershell
python run.py
```

### D. Running Backend Tests
Execute pytest with the virtual environment activated:
```powershell
pytest
```

---

## 4. Frontend Setup & Run

### A. Installing Node Packages
Install npm dependencies:
```bash
npm install
```

### B. Running Next.js Development Server
Start the frontend development server on `http://localhost:3000/`:
```bash
npm run dev
```

### C. Running Frontend Tests
Run Vitest suites:
```bash
npm run test
```
