# PlateauBreaker

PlateauBreaker is a small full-stack app for logging daily health metrics and detecting weight plateaus.

- Backend: FastAPI + SQLModel (SQLite)
- Frontend: Vue 3 + PrimeVue + Pinia + Chart.js

## Core features

- Record daily metrics: weight, sleep, calories, protein, exercise, steps, notes
- Dashboard KPIs (7-day averages) + trend charts (7/14/30 days)
- Plateau analysis (rules evaluated on the last 7 days)
- Cause analysis (top factors evaluated on the last 7 days)

## Repository layout

- `backend/`: FastAPI service (serves `/api/...`)
- `frontend/`: Vue app (Vite dev server + production build)
- `PlateauBreaker_Technical_Guide.md`: API + rules + data flow

## Prerequisites

- Node.js + npm (for the frontend)
- Python 3.11+ (for the backend)

## Quick start (local)

### 1) Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2) Frontend

```powershell
cd frontend
npm ci
npm run dev
```

The frontend dev server proxies `/api` to `http://localhost:8000` (see `frontend/vite.config.ts`).

## Production build (frontend)

```powershell
cd frontend
npm ci
npm run build
```

Build output is `frontend/dist/`.

## Tests

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
pytest -q
```

### Frontend

```powershell
cd frontend
npm ci
npm test
```

## Seed data (optional)

If you want sample records in your local SQLite database:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python seed_data.py
```

If the database already has records, the seed script exits without modifying data.

## What happens with no data?

- Dashboard shows an empty state prompting you to add records.
- Analysis requires **at least 5 recorded days within the last 7 calendar days (ending today)** to return meaningful results.

## Configuration (env vars)

### Backend

- `PLATEAUBREAKER_DB_PATH`
  - Optional.
  - Absolute path, or path relative to `backend/`.
  - Default: `backend/data/plateaubreaker.sqlite3`.

- `CORS_ORIGINS`
  - Optional.
  - Comma-separated list of allowed origins.
  - Default: `http://localhost:5173,http://127.0.0.1:5173`.

## Packaging a clean delivery zip

This repo contains a helper script to create a clean release zip (excluding `.git`, `node_modules`, `dist`, caches, venvs, and local DB files):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\make_release_zip.ps1
```

The zip is created under `release/`.

## Deployment notes (minimum)

- Serve the frontend (static `dist/`) and run the backend API.
- Ensure the backend has write access to the SQLite path (or set `PLATEAUBREAKER_DB_PATH`).
- Configure `CORS_ORIGINS` for your deployed frontend domain(s).
