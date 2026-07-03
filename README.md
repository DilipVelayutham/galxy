# GALXY Module 5: AI Preview Generation

This module handles the AI-powered preview generation for the GALXY Custom Lighting & Craft Studio platform. It orchestrates prompt building, interacts with an AI Provider (Gemini by default), caches responses, rate-limits usage, and uploads the generated images to Cloudinary.

## Setup Instructions

1. **Install dependencies:**
   Ensure you have a modern Python 3.10+ environment.
   ```bash
   pip install -r requirements.txt
   ```

2. **Run MongoDB:**
   The module expects a local or remote MongoDB instance to store generation logs, cache, and rate-limits.
   ```bash
   # Ensure mongod is running on mongodb://localhost:27017/
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory (where `wsgi.py` is located) with the following variables:

   ```env
   # Database
   MONGO_URI="mongodb://localhost:27017/galxy"
   
   # AI Provider Configuration
   AI_PROVIDER="gemini"
   GEMINI_API_KEY="your-gemini-api-key"
   
   # Rate Limiting & Timeout
   AI_FREE_GENERATIONS_PER_SESSION=5
   AI_MAX_GENERATIONS_PER_USER_PER_DAY=25
   AI_GENERATION_TIMEOUT_SECONDS=30
   
   # Cloudinary Configuration
   # If left blank, the module will mock uploads for local testing.
   CLOUDINARY_CLOUD_NAME="your-cloud-name"
   CLOUDINARY_API_KEY="your-api-key"
   CLOUDINARY_API_SECRET="your-api-secret"
   ```

4. **Run the Application:**
   ```bash
   python wsgi.py
   ```

## Running Tests
Run the test suite using pytest. The tests are configured to skip MongoDB index creation to keep execution time under 2 seconds.

```bash
# Sets TESTING=true automatically for fast execution if properly configured
pytest
```