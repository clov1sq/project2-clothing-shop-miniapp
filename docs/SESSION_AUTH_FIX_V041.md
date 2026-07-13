# Session authentication fix 0.4.1

The browser now sends API traffic through the frontend origin (`/api`) and the frontend production server proxies it to the existing backend URL from `VITE_API_URL`. This keeps the session cookie first-party inside Telegram WebView while preserving the existing Railway domains and variables.

The backend still supports direct credentialed requests from the configured `BACKEND_CORS_ORIGINS`, sets a host-only HttpOnly cookie, stores only the SHA-256 token hash, and rejects expired, revoked or blocked-user sessions.

Frontend bootstrap sequence:

1. `POST /api/v1/auth/telegram`;
2. wait for the response and cookie;
3. `GET /api/v1/auth/me`;
4. enable protected cart and favorites queries.

A protected request that later receives 401 triggers one single-flight Telegram re-authentication and one retry only.
