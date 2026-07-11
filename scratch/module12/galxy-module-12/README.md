# GALXY Module 12 - Admin Dashboard & Analytics

## Document 1 — Team Lead (Dashboard KPI Cards)
**Owner: Divakaran**

**Feature Owned:** Owns the four headline KPI StatCards on the admin dashboard home screen (Total Orders, Estimated Revenue, Pending Review Count, Pending Reviews To Moderate) and the shared aggregation orchestration inside the dashboard service that powers them. Also responsible for scaffolding the shared project infrastructure (Loading, Layout, API Client, Filter Bar, Error components) once, at project initialization, before any member starts feature work.

### Prerequisites
- Python 3.12+
- Node.js 22 LTS, npm 10+
- Access to the shared MongoDB Atlas cluster (request access from Team Lead)

### Setup
1. Clone the repo:
   `ash
   git clone https://github.com/galxy-org/galxy-module-12-dashboard.git
   cd galxy-module-12-dashboard
   `
2. Checkout this member's branch:
   `ash
   git checkout feature/module12-teamlead-kpi-dashboard
   `

### Backend Setup
`ash
cd backend
python -m venv venv
# activate venv (e.g. env\Scripts\activate on Windows)
pip install -r requirements.txt
cp .env.example .env
# fill in the real MONGO_URI (obtained privately from Team Lead) in .env
python run.py
`

### Frontend Setup
`ash
cd frontend
npm install
cp .env.example .env.local
# fill in NEXT_PUBLIC_API_BASE_URL (e.g. http://127.0.0.1:5000)
npm run dev
`

### Exact Endpoint(s) Owned
**GET /api/admin/dashboard/stats**

**Note to PM/Team Lead:**
*I added an automatic redirect from / to /admin for dev convenience. Please confirm this addition aligns with product expectations.*

**Sample Request:**
`http
GET /api/admin/dashboard/stats?date_from=2026-06-01&date_to=2026-06-30
`

**Response JSON:**
`json
{
  "success": true,
  "message": "Stats retrieved successfully",
  "data": {
    "total_orders_in_range": 150,
    "estimated_revenue_in_range": 45000,
    "pending_review_count": 12,
    "pending_reviews_to_moderate": 5
  }
}
`

### Tests
Tests are configured to verify that the GET /api/admin/dashboard/stats route returns a 200 with all four KPI fields populated correctly against seed data. Also ensures default date handling works correctly.

### Ownership List
**Owns Exclusively:**
- pp/services/dashboard_service.py (orchestration function + KPI aggregations)
- rontend/app/admin/page.tsx (KPI card section)
- rontend/components/admin/StatCard.tsx
- rontend/components/shared/Loading.tsx, Layout.tsx, ApiClient.ts, FilterBar.tsx, ErrorState.tsx (one-time creation)

**Shared files (coordinate before editing):**
- pp/services/dashboard_service.py (Member 2 also edits)
- pp/routes/admin_dashboard_routes.py (Members 3 and 4 will register their routes)
- rontend/app/admin/page.tsx (Member 2 adds the chart section)

---

## Document 2 — Member 2 (Dashboard Charts)

**Feature owned:** Own the Dashboard Charts portion of Module 12: the Orders By Status and Top Categories visualizations on the admin dashboard home screen, and the corresponding aggregation logic inside the shared dashboard_service.py file.

### Prerequisites
- Python 3.x
- Node.js
- npm
- Access to the shared MongoDB Atlas cluster (request access from Team Lead)

### Setup
1. Clone the repo
2. Checkout this member's branch: eature/module12-member2-dashboard-charts

### Backend setup
`ash
cd backend/
python -m venv venv
# activate venv
pip install -r requirements.txt
cp .env.example .env
# fill in the real MONGO_URI (obtained privately from Team Lead)
python run.py
`

### Frontend setup
`ash
cd frontend/
npm install
cp .env.example .env.local
# fill in NEXT_PUBLIC_API_BASE_URL
npm run dev
`

### Exact endpoint(s) owned
**GET /api/admin/dashboard/stats**

Sample Request:
`http
GET /api/admin/dashboard/stats?date_from=2026-06-01&date_to=2026-06-30
`

Response JSON (includes Team Lead's stats + Member 2's charts):
`json
{
  "success": true,
  "message": "Stats retrieved successfully",
  "data": {
    "total_orders_in_range": 150,
    "estimated_revenue_in_range": 45000,
    "pending_review_count": 12,
    "pending_reviews_to_moderate": 5,
    "orders_by_status": [
      { "status": "received", "count": 10 },
      { "status": "reviewed", "count": 5 },
      { "status": "quote_sent", "count": 0 },
      { "status": "confirmed", "count": 0 },
      { "status": "in_production", "count": 0 },
      { "status": "ready", "count": 0 },
      { "status": "out_for_delivery", "count": 0 },
      { "status": "delivered", "count": 0 },
      { "status": "cancelled", "count": 0 }
    ],
    "top_categories": [
      { "category_name": "Lighting", "order_count": 50 }
    ]
  }
}
`

Note: the JSON above shows the eventual MERGED response after the Team Lead's
KPI fields are combined with this member's orders_by_status/top_categories.
In this repo in isolation, get_dashboard_stats_data() returns only
orders_by_status and top_categories.

### Tests
Run tests locally via pytest in the ackend folder. The tests verify the unified response format including the new aggregations.

### Ownership List
**Owns Exclusively:**
- rontend/components/admin/OrdersByStatusChart.tsx
- rontend/components/admin/TopCategoriesChart.tsx
- pp/services/dashboard_service.py (orders_by_status + top_categories aggregation functions only)

**Shared files:**
- pp/services/dashboard_service.py (Team Lead also edits this file; agree on merge points)
- rontend/app/admin/page.tsx (Team Lead adds KPI section)

---

## Document 3 - Member 3 (Product Analytics)

### 1. Feature Owned
The Product Analytics feature provides a dashboard interface for administrators to evaluate catalog item performances. It aggregates metrics like product views, wishlist additions, actual order counts, and calculates a directional conversion rate per product, supporting category, date-range, and sorting filters.

### 2. Prerequisites
- **Python**: Version 3.12+ (Backend API development)
- **Node.js**: Version 22 LTS (Frontend Next.js application)
- **npm**: Version 10+ (Frontend package manager)
- **Database**: Access permissions to the shared MongoDB Atlas cluster (request from Team Lead)

### 3. Setup
1. Clone the repository:
   `ash
   git clone https://github.com/Divakaran41/galxy-module-12-dashboard.git
   `
2. Checkout your assigned branch:
   `ash
   git checkout assignment-shanmugam
   `

### 4. Backend Setup
1. Move to the backend folder and create a virtual environment:
   `ash
   cd backend
   python -m venv venv
   `
2. Activate the virtual environment:
   - **Windows**: .\venv\Scripts\activate
   - **macOS/Linux**: source venv/bin/activate
3. Install dependencies:
   `ash
   pip install -r requirements.txt
   `
4. Copy the environment template:
   `ash
   cp .env.example .env
   `
5. Configure the real MONGO_URI (obtained securely from the Team Lead) and database name in ackend/.env.
6. Run the Flask application:
   `ash
   python run.py
   `

### 5. Frontend Setup
1. Move to the frontend folder:
   `ash
   cd ../frontend
   `
2. Install package dependencies:
   `ash
   npm install
   `
3. Copy the environment configuration:
   `ash
   cp .env.example .env.local
   `
4. Confirm NEXT_PUBLIC_API_BASE_URL is set to point to the local backend port (usually http://localhost:5000 or http://localhost:8000).
5. Launch the Next.js development server:
   `ash
   npm run dev
   `

### 6. Exact Endpoint Owned
* **URL**: /api/admin/analytics/products
* **Method**: GET
* **Query Parameters**:
  - category_id (string, optional) - Filter products by category.
  - date_from (string, optional) - ISO 8601 start timestamp for order filtering.
  - date_to (string, optional) - ISO 8601 end timestamp for order filtering.
  - sort (string, optional) - Sort products by "views" | "wishlist_adds" | "orders" (descending).
  - page (int, optional) - Current pagination page. Default 1.
  - limit (int, optional) - Count of records per page. Default 10.
* **Security**: Enforced with @require_admin decorator.

#### Sample Request
`http
GET /api/admin/analytics/products?sort=views&page=1&limit=5 HTTP/1.1
Host: localhost:5000
`

#### Sample Response JSON
`json
{
  "success": true,
  "data": [
    {
      "product_id": "64b1f4c5e3d7a82b98e12345",
      "title": "Luxury Lamp",
      "category_name": "Lamps & Lighting",
      "views": 2500,
      "wishlist_count": 80,
      "order_count": 25,
      "conversion_rate": 0.01
    }
  ],
  "page": 1,
  "limit": 5,
  "total": 1,
  "totalPages": 1
}
`

### 7. Running Tests
Run the unit test suite locally to verify pipeline aggregation states and mock database interfaces:
- **Windows**:
  `powershell
  ="backend"; py -m unittest backend/tests/test_product_analytics.py
  `
- **macOS/Linux**:
  `ash
  PYTHONPATH=backend python -m unittest backend/tests/test_product_analytics.py
  `
The tests cover:
- Database query aggregations with empty collections.
- Correct calculations of views, wishlist additions, order counts, and conversion rates.
- Pagination bounds, category-specific matching filters, and date range checks inside child aggregation lookup pipelines.

### 8. Ownership Boundaries
- **Exclusively Owned (modify freely)**:
  - ackend/app/services/product_analytics_service.py
  - ackend/tests/test_product_analytics.py
  - rontend/app/admin/analytics/products/page.tsx
  - rontend/components/admin/ProductAnalyticsTable.tsx
- **Shared Files (coordinate before editing)**:
  - ackend/app/routes/admin_dashboard_routes.py (Add new routes strictly under the designated routes blueprint without modifying existing endpoints).

---

## Document 4 - Member 4 (AI Usage Analytics)

### 1. Feature Owned
The AI Usage Analytics feature provides a dashboard interface for administrators to monitor the performance, volume, and success rates of automated AI model generations. It tracks critical metrics such as total generations, successful vs. failed operations, average generation latency, and cache hit rates (when cache tracking is active). It also breaks down generation volumes by model categories, helping administrators manage backend costs and identify user interests.

**Coordination Flag**:
* cache_hit_rate is coded but returns null until Module 5 adds served_from_cache to ai_generations — flagged to Module 5's team.

### 2. Prerequisites
- **Python**: Version 3.12+ (Backend API development)
- **Node.js**: Version 22 LTS (Frontend Next.js application)
- **npm**: Version 10+ (Frontend package manager)
- **Database**: Access permissions to the shared MongoDB Atlas cluster (request from Team Lead)

### 3. Setup
1. Clone the repository:
   `ash
   git clone https://github.com/Divakaran41/galxy-module-12-dashboard.git
   cd galxy-module-12-dashboard
   `
2. Checkout your assigned branch:
   `ash
   git checkout priya
   `

### 4. Backend Setup
1. Move to the backend folder and create a virtual environment:
   `ash
   cd backend
   python -m venv venv
   `
2. Activate the virtual environment:
   - **Windows**: .\venv\Scripts\activate
   - **macOS/Linux**: source venv/bin/activate
3. Install dependencies:
   `ash
   pip install -r requirements.txt
   `
4. Copy the environment template:
   `ash
   cp .env.example .env
   `
5. Configure the real MONGO_URI (obtained securely from the Team Lead) and database name in ackend/.env.
6. Run the Flask application:
   `ash
   python run.py
   `

### 5. Frontend Setup
1. Move to the frontend folder:
   `ash
   cd ../frontend
   `
2. Install package dependencies:
   `ash
   npm install
   `
3. Copy the environment configuration:
   `ash
   cp .env.example .env.local
   `
4. Confirm NEXT_PUBLIC_API_BASE_URL is set to point to the local backend port (usually http://localhost:5000 or http://localhost:8000).
5. Launch the Next.js development server:
   `ash
   npm run dev
   `

### 6. Exact Endpoint Owned
* **URL**: /api/admin/analytics/ai-usage
* **Method**: GET
* **Query Parameters**:
  - category_id (string, optional) - Filter logs by a specific category.
  - date_from (string, optional) - ISO 8601 start timestamp.
  - date_to (string, optional) - ISO 8601 end timestamp.
* **Security**: Enforced with @require_admin decorator.

#### Sample Request
`http
GET /api/admin/analytics/ai-usage?category_id=64b1f4c5e3d7a82b98e12345&date_from=2026-07-01T00:00:00Z&date_to=2026-07-31T23:59:59Z HTTP/1.1
Host: localhost:5000
`

#### Sample Response JSON
`json
{
  "success": true,
  "data": {
    "total_generations": 1250,
    "successful": 1200,
    "failed": 50,
    "avg_generation_time_ms": 320.5,
    "cache_hit_rate": 0.154,
    "generations_by_category": [
      {
        "category_id": "64b1f4c5e3d7a82b98e12345",
        "category_name": "Lamps & Lighting",
        "count": 800
      },
      {
        "category_id": "64b1f4c5e3d7a82b98e54321",
        "category_name": "Craft Patterns",
        "count": 450
      }
    ]
  }
}
`

### 7. Running Tests
Run the unit test suite locally to verify pipeline aggregation states and mock database interfaces:
- **Windows**:
  `powershell
  ="backend"; python -m unittest backend/tests/test_ai_usage_analytics.py
  `
- **macOS/Linux**:
  `ash
  PYTHONPATH=backend python -m unittest backend/tests/test_ai_usage_analytics.py
  `
The tests cover:
- Database query aggregations with empty collections.
- Correct calculations of success, failure, total generations, and average response times.
- Dynamic omission of cache_hit_rate if the served_from_cache tracking field has not yet been introduced by Module 5.

### 8. Ownership Boundaries
- **Exclusively Owned (modify freely)**:
  - ackend/app/services/ai_usage_analytics_service.py
  - ackend/tests/test_ai_usage_analytics.py
  - rontend/app/admin/analytics/ai-usage/page.tsx
  - rontend/components/admin/AIUsageStats.tsx
- **Shared Files (coordinate before editing)**:
  - ackend/app/routes/admin_dashboard_routes.py (Add new routes strictly under the designated routes blueprint without modifying existing endpoints).
