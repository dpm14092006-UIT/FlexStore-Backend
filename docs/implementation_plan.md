# Deployment & Database Integration Plan

## Goal Description
The goal is to deploy the FlexStore 3D web application to a server and connect it to a persistent database.
We will:
1.  **Add Supabase (PostgreSQL)** database to store optimization history.
2.  **Deploy Backend** (FastAPI) to **Render** (Free Tier).
3.  **Deploy Frontend** (React/Vite) to **Vercel** (Free Tier).

## User Review Required
> [!TIP]
> **Why Supabase?**: Supabase *is* PostgreSQL but comes with a beautiful dashboard to view your data, a built-in API, and a generous free tier. It is much easier to manage than a raw PostgreSQL server.
>
> **Action Required**: You will need to create a free account on [Supabase.com](https://supabase.com) and get the `DATABASE_URL`.

## Proposed Changes

### Backend Configuration
#### [NEW] `backend/app/config.py`
-   Manage environment variables (`DATABASE_URL`, `CORS_ORIGINS`).

#### [NEW] `backend/app/database.py`
-   Setup SQLAlchemy engine and session management.

#### [NEW] `backend/app/models/sql_models.py`
-   Define SQL tables for `OptimizationRequest` and `OptimizationResult`.

#### [MODIFY] [requirements.txt](file:///d:/LogisticArirbnb/backend/requirements.txt)
-   Add `sqlalchemy`, `psycopg2-binary`, `python-dotenv`.

#### [MODIFY] [main.py](file:///d:/LogisticArirbnb/backend/app/main.py)
-   Initialize database connection on startup.
-   Read `CORS_ORIGINS` from environment variables.
-   **Note**: We will use standard SQLAlchemy to connect to Supabase (it works just like any Postgres DB).

#### [MODIFY] [endpoints.py](file:///d:/LogisticArirbnb/backend/app/api/endpoints.py)
-   Update `/optimize` endpoint to save inputs and results to the database.

### Deployment Configuration
#### [NEW] `backend/Procfile`
-   For Render: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Configuration
#### [MODIFY] [api.js](file:///d:/LogisticArirbnb/frontend/src/services/api.js)
-   Update base URL to use `import.meta.env.VITE_API_URL`.

#### [NEW] `frontend/vercel.json`
-   Configuration for Vercel deployment (routing rules).

## Verification Plan

### Locally
1.  Connect backend to Supabase (using remote URL).
2.  Verify `/optimize` saves data, and it appears in the Supabase Dashboard.

### Deployment
1.  Push code to GitHub.
2.  Connect to Render (Backend) and Vercel (Frontend).
3.  Verify live URL functionality.
