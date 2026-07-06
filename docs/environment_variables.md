# Environment Variable Documentation

This document defines the environment configurations required by the security and password recovery layer (Module 1, In3).

## SMTP Outbound Mail Configurations

These variables are required to enable sending password-reset links to users via SMTP.

| Variable | Type | Description | Owner | Coordination Notes |
| :--- | :--- | :--- | :--- | :--- |
| `SMTP_HOST` | String | The hostname of the outbound mail server (e.g., `smtp.gmail.com`). | In3 (Tharani) | Shared and coordinated with **Module 11 (Notifications)** to prevent duplicate connections. |
| `SMTP_PORT` | Integer | Outbound SMTP connection port (e.g., `587` for TLS, `465` for SSL). | In3 (Tharani) | Coordinated with **Module 11**. |
| `SMTP_EMAIL` | String | The sender email address used for recovery correspondence. | In3 (Tharani) | Coordinated with **Module 11**. |
| `SMTP_PASSWORD`| String | Credentials/API key for the SMTP server account. | In3 (Tharani) | **Never logged** or printed anywhere in plaintext. |

---

## Database Configurations

These variables establish database connections for rate limiting and recovery token storage.

| Variable | Type | Description | Owner | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MONGO_URI` | String | Full MongoDB connection string (e.g. `mongodb+srv://...` for Atlas or `mongodb://localhost:27017` for local). | Shared / In1 | Must support `tlsCAFile` configuration for SSL Atlas connection. |
| `DATABASE_NAME` | String | Target MongoDB database name (default: `galxy`). | Shared / In1 | Shared across all Module 1 developers. |

---

## Security Configurations

| Variable | Type | Description | Owner | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `ALLOWED_ORIGINS`| CSV String | Permitted cross-origin hosts (e.g. `http://localhost:3000`). | In1 | The recovery services use the first origin listed here to construct the forgot-password reset link. |

---

## Local Development Mock Fallback

If `SMTP_HOST`, `SMTP_PORT`, `SMTP_EMAIL`, or `SMTP_PASSWORD` are left unconfigured, the application falls back to a development SMTP mock:
1. It simulates the delay of sending an email.
2. It outputs a masked log representation to the console:
   `Reset Link (Masked): http://localhost:3000/reset-password?token=a8G9fD...`
3. No plaintext tokens are printed, satisfying security logging policies.
