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

### Node version (required for reproducible installs)

- This repo pins Node via `D:\\git\\plateau-breaker\\.nvmrc` (`20.19.0`).
- If you use asdf, you can use `D:\\git\\plateau-breaker\\.tool-versions`.
- The frontend also declares `engines.node` in `D:\\git\\plateau-breaker\\frontend\\package.json`.
- Use Node 20.19+ to avoid lockfile drift and ensure `npm ci` works in a clean environment.
- The frontend enforces this via `D:\\git\\plateau-breaker\\frontend\\.npmrc` (`engine-strict=true`), so `npm ci` fails fast on the wrong Node version.

#### Example (nvm)

```powershell
nvm install 20.19.0
nvm use 20.19.0
node -v
```

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

Note: the frontend ships with `frontend/.npmrc` to keep the npm cache inside `frontend/.npm-cache`. This avoids relying on a global user cache in restricted environments; the cache is safe to delete and excluded from commits/releases.

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

## CI (recommended)

- GitHub Actions workflow: `D:\\git\\plateau-breaker\\.github\\workflows\\ci.yml`
- Runs frontend `npm ci`, `npm test -- --run`, `npm run build` using Node 20 (from `.nvmrc`), plus backend `pytest -q` on Python 3.11.

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

## KPI definitions (quick reference)

- `weight_change_7d`: only available when you have a record for **today** and **exactly 7 days ago**; otherwise it is `null`.

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

This repo contains a helper script to create a clean release zip.

Release contents (deployable):
- `backend/` (source, excludes `backend/tests` and local `backend/data`)
- `frontend/dist/` (production build output)
- `README.md`

```powershell
# Optional: clean local build artifacts first
powershell -ExecutionPolicy Bypass -File .\scripts\clean_artifacts.ps1

powershell -ExecutionPolicy Bypass -File .\scripts\clean_artifacts.ps1 -All

# Build frontend first (required for packaging)
cd frontend
npm ci
npm run build
cd ..

powershell -ExecutionPolicy Bypass -File .\scripts\make_release_zip.ps1
```

The zip is created under `release/`.

## Deployment notes (minimum)

- Serve the frontend (static `dist/`) and run the backend API.
- Ensure the backend has write access to the SQLite path (or set `PLATEAUBREAKER_DB_PATH`).
- Configure `CORS_ORIGINS` for your deployed frontend domain(s).
