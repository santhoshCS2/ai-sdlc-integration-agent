
# coastalsevel Frontend

Professional, scalable frontend architecture for the coastalsevel Autonomous SDLC Platform.

## Architecture

 This project follows a feature-based, configuration-driven architecture:

```
src/
 ├── api/           # Centralized API handling (Axios, Endpoints, Services)
 ├── components/    # Reusable UI components
 ├── config/        # Environment and App configuration
 ├── constants/     # Static constants (Routes, Messages, Options)
 ├── contexts/      # React Contexts (Auth, Theme)
 ├── hooks/         # Custom React Hooks
 ├── pages/         # Page Views
 ├── utils/         # Helpers (PDF generation, Formatting)
 └── types/         # TypeScript definitions
```

## Setup

1.  **Install dependencies**:
    ```bash
    npm install
    ```

2.  **Environment Setup**:
    Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
    Update `VITE_API_BASE_URL` if your backend is running elsewhere.

3.  **Run Development Server**:
    ```bash
    npm run dev
    ```

## Key Features

*   **Config-Driven**: All endpoints, routes, and agents are defined in `src/constants` and `src/config`.
*   **Service Layer**: API logic is separated from UI components in `src/api/services`.
*   **Type Safety**: Full TypeScript support with shared types.
*   **Secure**: Centralized Auth logic in `AuthService` and `useAuth` hook.
