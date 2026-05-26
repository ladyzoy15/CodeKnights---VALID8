# Google Authentication Integration

This document describes the "Continue with Google" authentication flow, auto-registration, and onboarding process implemented in the Aura system.

## Overview

The integration allows users to sign in using their Google accounts. If a user is new to the system, they are automatically registered with a **Student** role and prompted to select their school through an onboarding modal.

## Backend Components

### 1. Authentication Router (`Backend/app/routers/auth.py`)
- **Endpoint**: `POST /auth/google`
- **Logic**:
    - Validates the Google ID Token provided by the frontend.
    - Checks if a user with the Google email already exists.
    - If the user exists, returns an access token.
    - If the user does not exist:
        - If `school_id` is provided, creates a new user with the **Student** role linked to that school.
        - If `school_id` is NOT provided, returns `needs_onboarding: true` along with the user's basic info (email, name).

### 2. School Router (`Backend/app/routers/school.py`)
- **Endpoint**: `GET /schools/list` (Public)
- **Logic**: Returns a list of all active schools. This is used by the onboarding modal for unauthenticated users.

## Frontend Components

### 1. Login View (`src/views/desktop/auth/LoginView.vue`)
- Integrates the Google Identity Services (`gsi/client`) script.
- Displays the "Continue with Google" button (forced to English locale).
- Handles the Google callback and triggers the authentication flow.

### 2. Onboarding Modal (`src/components/desktop/auth/GoogleOnboardingModal.vue`)
- Displayed when a new user signs in with Google.
- Allows the user to select their school from the public school list.
- Finalizes the registration process.

### 3. Auth Composable (`src/composables/useAuth.js`)
- `loginWithGoogleAuth(idToken, schoolId)`: Communicates with the backend to perform login or registration.
- Manages session persistence using `localStorage` (`aura_token`).

## Configuration

The following environment variables are required in the `.env` file:

```env
GOOGLE_LOGIN_ENABLED=true
GOOGLE_WEB_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

### Note on Runtime Configuration
The frontend uses a `runtime-config.js` mechanism. Ensure that `runtime-config.js.template` and the entrypoint script (`docker-entrypoint.d/40-runtime-config.sh`) are updated to include these Google variables.

## Testing

1. Ensure the containers are running: `docker-compose up -d`.
2. Navigate to the login page (`http://localhost:5175/login`).
3. Click "Continue with Google".
4. If it's a new account, verify that the onboarding modal appears and allows school selection.
5. After selection, verify that the user is redirected to the dashboard.
6. Verify session persistence by refreshing the page or reopening the browser.
