# Frontend Review & Testimonial Integration Guide (Module 9C)

This document provides setup, config boundaries, and detailed integration documentation for Module 9C (Review & Testimonial UI) components.

---

## 1. Backend REST Endpoints & Contracts

### 1.1 GET `/api/products/:id/reviews`
*   **Access**: Public (no token needed).
*   **Query Params**:
    *   `page`: Page index (default: `1`)
    *   `limit`: Page size (default: `20`)
    *   `sort`: Sort options (`"newest"` | `"highest_rated"` | `"lowest_rated"`)
*   **Response Shape**:
    ```json
    {
      "success": true,
      "data": [
        {
          "_id": "60c72b2f9b1d8b1f00000201",
          "customer_name": "Rohan",
          "rating": 5,
          "comment": "Spectacular neon glow! Quality is fantastic.",
          "images": ["https://res.cloudinary.com/.../img.jpg"],
          "created_at": "2026-07-04T12:00:00.000Z"
        }
      ],
      "page": 1,
      "limit": 5,
      "total": 1,
      "totalPages": 1
    }
    ```
*   **Security Constraint**: Does *not* return `user_id` or `order_id` fields.

### 1.2 POST `/api/products/:id/reviews`
*   **Access**: Authenticated (Requires Bearer JWT token in headers).
*   **Headers**: `Authorization: Bearer <access_token>`
*   **Body Content**:
    ```json
    {
      "rating": 5,
      "comment": "Vibrant colors, fast delivery!",
      "images": ["https://res.cloudinary.com/.../img.jpg"]
    }
    ```
*   **Response Statuses**:
    *   `201 Created`: Review received, sets `is_approved: false`.
    *   `403 Forbidden`: User has no verified delivered purchase of the product.
    *   `409 Conflict`: User has already reviewed this product purchase.

### 1.3 POST `/api/admin/media/upload` (CMS Upload Helper)
*   **Access**: Authenticated (Requires Bearer JWT token in headers).
*   **Body Content**: Multipart `FormData` containing a `file` field.
*   **Response Shape**:
    ```json
    {
      "success": true,
      "url": "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    }
    ```

---

## 2. Reusable UI Components API

### 2.1 `<StarRating>`
Renders star ratings. Supports dual mode: read-only average display and interactive user inputs.
*   **Imports**:
    ```tsx
    import { StarRating } from "@/components/reviews/StarRating";
    ```
*   **Properties**:
    | Property | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `rating` | `number` | *Required* | Current numerical score (supports decimals for read-only). |
    | `interactive` | `boolean` | `false` | Sets keyboard focus (role="slider") and hover clicks. |
    | `onChange` | `(r: number) => void` | `undefined` | Callback fired on rating selection. |
    | `size` | `number` | `20` | Pixel height/width sizing of individual stars. |

### 2.2 `<ReviewForm>`
Customer review submission form with gated uploads and validation alerts.
*   **Imports**:
    ```tsx
    import { ReviewForm } from "@/components/reviews/ReviewForm";
    ```
*   **Properties**:
    | Property | Type | Description |
    | :--- | :--- | :--- |
    | `productId` | `string` | The unique MongoDB identifier of the target product. |
    | `onSuccess` | `() => void` | Callback triggered after a review compiles and submits successfully. |

### 2.3 `<ReviewList>`
Verified reviews display panel on the product page. Handles paging, sorting, loading skeletons, and error retries.
*   **Imports**:
    ```tsx
    import { ReviewList } from "@/components/reviews/ReviewList";
    ```
*   **Properties**:
    | Property | Type | Description |
    | :--- | :--- | :--- |
    | `productId` | `string` | The unique MongoDB identifier of the product. |
    | `refreshTrigger` | `number` | Numerical trigger incremented to force refetches (e.g., when a review is submitted). |

---

## 3. Global Context Dependencies

These components rely on the following client context wrappers defined in [layout.tsx](file:///d:/review%20rating/frontend/app/layout.tsx):

1.  **`AuthProvider`** (`@/context/AuthContext`): Checks if users are logged in, hydrates credentials via silent token refreshes, and exposes authorization state.
2.  **`ToastProvider`** (`@/context/ToastContext`): Renders bottom-right system feedback alerts using lucide-react icons and Framer Motion.

---

## 4. Visual Styles (Void Black / Neon Glow Theme)

Ensure the custom utilities are present in [globals.css](file:///d:/review%20rating/frontend/app/globals.css) before compilation:

*   **Void Black Base**: `#0B0B0F`
*   **Panel Charcoal**: `#16161C`
*   **Glassmorphism**: `.glass-panel { background: rgba(22, 22, 28, 0.7); backdrop-filter: blur(12px); ... }`
*   **Glow Utilities**: `.glow-blue`, `.glow-pink`, `.glow-violet`, `.glow-yellow`
