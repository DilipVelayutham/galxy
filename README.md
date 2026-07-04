# GALXY - Module 1

## Branch
`in3-tharani`

## Owner
**Tharani Jayaprakash**
Security & Password Recovery Developer

## Responsibilities & Deliverables

### Backend
- **Password Helper** (`backend/app/utils/password_helper.py`): Secure password hashing and verification using `bcrypt` with a cost factor of 12.
- **Validators** (`backend/app/utils/validators.py`): Shared input validation checks for emails, passwords, Indian mobile numbers, and pincodes.
- **Rate Limiter** (`backend/app/utils/rate_limiter.py`): Custom MongoDB-backed forgot-password rate limiter decorator (5 requests / 15 minutes per IP+email).
- **Forgot & Reset Password Flows** (`backend/app/services/auth_service.py` & `backend/app/routes/auth_routes.py`): API route handlers and service operations implementing secure recovery logic, timing-attack mitigations, and contract-correct error field mappings.

### Frontend
- **Forgot Password Page** (`frontend/app/(public)/forgot-password/page.tsx`): Dark glassmorphism recovery request form, designed for complete enumeration safety.
- **Reset Password Page** (`frontend/app/(public)/reset-password/page.tsx`): Password update page validating recovery tokens and new credentials.
- **Shared Validators Module** (`frontend/lib/validators.ts`): Client-side validators mirroring backend validators.

## Project Documentation
All documentation requested in the Module 1 Execution contract is stored in the `docs/` folder:
*   **Environment Variable Documentation**: [docs/environment_variables.md](docs/environment_variables.md)
*   **Security Compliance Test Report**: [docs/security_test_report.md](docs/security_test_report.md)

## Workflow & Guidelines
Develop → Commit → Test → Pull Request to `dev`

Keep all password recovery flows secure, predictable, and consistent.