# Deployment Walkthrough

## 1. Push Code to GitHub
Ensure all your latest changes (including config files) are on GitHub.
Run these commands in your potentially new terminal:
```bash
git add .
git commit -m "Configure deployment and database"
git push
```

## 2. Deploy Backend (Render.com)
1.  Go to [dashboard.render.com](https://dashboard.render.com) -> **New +** -> **Web Service**.
2.  Connect your GitHub repo `LogisticAireBNB`.
3.  **Settings**:
    *   **Name**: `flexstore-backend` (or similar)
    *   **Region**: Singapore (SG)
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r backend/requirements.txt`
    *   **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables** (Advanced):
    *   Add `DATABASE_URL` = `postgresql://postgres:logisticairbnb@db.yqzpygtagxpzhlzojecz.supabase.co:5432/postgres`
    *   Add `CORS_ORIGINS` = `*` (Or your Vercel URL later)
    *   Add `PYTHON_VERSION` = `3.10.0` (Optional, recommended)
5.  Click **Create Web Service**. Wait for it to be "Live".
6.  **Copy the Backend URL** (e.g., `https://flexstore-backend.onrender.com`).

## 3. Deploy Frontend (Vercel)
1.  Go to [vercel.com](https://vercel.com) -> **Add New...** -> **Project**.
2.  Import `LogisticAireBNB`.
3.  **Configure Project**:
    *   **Framework Preset**: Vite
    *   **Root Directory**: Click `Edit` -> Select `frontend`.
4.  **Environment Variables**:
    *   Name: `VITE_API_URL`
    *   Value: *Paste your Render Backend URL here* (no trailing slash, e.g., `https://flexstore-backend.onrender.com`).
5.  Click **Deploy**.

## 4. Final Verification
1.  Open your Vercel URL.
2.  Try adding an item and clicking **Optimize Loading**.
3.  If it works and you see results, the entire flow (Frontend -> Backend -> Database) is operational!
