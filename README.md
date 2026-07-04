# GALXY - Module 9A Backend: Reviews

This repository implements **Sub-Module 9A – Backend: Reviews** in Flask + MongoDB. The Reviews module provides customer product reviews, rating rollup calculation (updating product review stats dynamically), image uploads, and admin moderation features.

## Architecture & Responsibilities

- **Models** (`backend/app/models/review.py`): Defines the MongoDB review schema and serializes outputs. Supports a `public=True` serialization option that hides private user identity fields (`user_id`, `order_id`).
- **Services**:
  - `review_service.py`: Contains core review flows, verifying purchase checks, duplicate checks, image uploads, moderation (approving, rejecting, deleting), and promoting reviews to testimonials.
  - `rating_rollup_service.py`: Calculates average ratings and review counts from approved reviews, updating the products database collection.
- **Routes**:
  - `review_routes.py`: Registers public review endpoints: review submissions and public approved reviews queries.
  - `admin_review_routes.py`: Registers admin moderation endpoints: approve, reject, delete, list, and promote reviews to testimonials.

## Integration & Dependencies

This module strictly coordinates with the following components:
1. **Module 8 (Order Service)**: Consumes the `order_service.has_delivered_order_for_product(user_id, product_id)` helper. If Module 8 is unavailable, review submission returns a `500` integration error.
2. **Module 10 (Cloudinary Upload Helper)**: Consumes the upload helper for image file uploads. If unavailable, file upload attempts return a `500` integration error.
3. **Module 3 (Products Collection)**: Updates fields `rating_avg` and `rating_count` under the product document. No other product fields are modified.
4. **Module 1 (User Profiles)**: Snapshots client name from user profiles during review submission.
5. **Testimonials Collection**: Writes promoted review data directly into the `testimonials` collection.

---

## Configuration & Environment Variables

Create a `backend/.env` file with the following variables:
```env
FLASK_ENV=development
MONGO_URI=mongodb+srv://snehaharikrishnan5_db_user:<db_password>@cluster0.s6yb2yr.mongodb.net/reviews_db?appName=Cluster0
DB_NAME=reviews_db
JWT_SECRET=default_jwt_secret_key_12345
JWT_ALGORITHM=HS256
PORT=5000
```
Ensure you replace `<db_password>` with the actual database access password.

## Installation

Install the required Python dependencies:
```bash
pip install -r backend/requirements.txt
```

## How to Run

Start the Flask development server:
```bash
py backend/run.py
```

## How to Test

Run the unit test suite:
```bash
$env:PYTHONPATH="backend"; py -m pytest backend/tests/test_reviews.py
```
All unit tests are executed using an in-memory `mongomock` client.