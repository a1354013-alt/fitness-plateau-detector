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
  - `backend/data/`: default local SQLite location for development/runtime data; not part of the release artifact
  - `backend/alembic/` + `backend/alembic.ini`: migration entrypoint for schema changes
- `frontend/`: Vue app (Vite dev server + production build)
- `PlateauBreaker_Technical_Guide.md`: API + rules + data flow

## Prerequisites

- Node.js + npm (for the frontend)
- Python 3.11 (for the backend; CI uses 3.11)

### Node version (required for reproducible installs)

- This repo pins Node via `.nvmrc` (`20.19.0`).
- If you use asdf, you can use `.tool-versions`.
- The frontend also declares `engines.node` in `frontend/package.json`.
- Use Node 20.19+ to avoid lockfile drift and ensure `npm ci` works in a clean environment.
- The frontend enforces this via `frontend/.npmrc` (`engine-strict=true`), so `npm ci` fails fast on the wrong Node version.

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
python -m pip install -r requirements.txt -c constraints.txt
python -m pip install -r requirements-dev.txt -c constraints.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2) Frontend

```powershell
cd frontend
npm ci
npm run dev
```

By default, the frontend calls `/api` (see `frontend/src/services/api.ts`).

- In dev, Vite proxies `/api` to `http://localhost:8000` (see `frontend/vite.config.ts`).
- In production, you can override the API base via `VITE_API_BASE_URL` (see `.env.example`).

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
python -m pip install -r requirements.txt -c constraints.txt
python -m pip install -r requirements-dev.txt -c constraints.txt
pytest -q
```

### Frontend

```powershell
cd frontend
npm ci
npm test
```

## CI (recommended)

- GitHub Actions workflow: `.github/workflows/ci.yml`
- Frontend job runs `npm ci`, `npm test -- --run`, `npm run build`, then a release packaging smoke test:
  - `python scripts/make_release_zip.py --out-dir release`
  - `python scripts/validate_release_zip.py --out-dir release`
- Backend job runs `pytest -q` on Python 3.11 using the locked dependency set from `constraints.txt`.

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
- If your latest record is **more than 7 days old**, the Dashboard shows a **stale** warning to avoid misleading interpretation of “latest” metrics.

## KPI definitions (quick reference)

- `weight_change_7d`: only available when you have a record for **today** and **exactly 7 days ago**; otherwise it is `null`.

## Configuration (env vars)

See `.env.example` for a starting point.

### Backend

- `PLATEAUBREAKER_DB_PATH`
  - Optional.
  - Absolute path, or a path relative to `backend/` (example: `data/plateaubreaker.sqlite3`).
  - Default: `backend/data/plateaubreaker.sqlite3`.
  - `backend/data/` is a local runtime data directory, not a deployable asset. Release zips must not include it.

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

Cross-platform alternative (works on Linux/macOS/Windows):

```bash
python scripts/make_release_zip.py --out-dir release
python scripts/validate_release_zip.py --out-dir release
```

### Source package vs release package

- **Source package** (for development backup/review): contains the repository source tree. If you must zip it, run `scripts/clean_artifacts.ps1 -All`
  and exclude working-directory traces like `.git`, `node_modules/`, `dist/`, `.npm-cache/`, `__pycache__/`, IDE folders, and local databases.
- A workspace/source zip may still contain review-only or machine-local traces such as `.git`, `.vscode`, local SQLite data, and other developer context. Treat it as source material, not a formal deliverable.
- **Release package** (formal delivery / deployment): use the release zip generated by the scripts above. It is intentionally strict and contains only
  deployable content (`backend/` source including Alembic migration files + `frontend/dist/` + `README.md`).
- Formal handoff, deployment, and external sharing should always use the generated release zip under `release/`, not an ad-hoc source zip.

## Deployment notes (minimum)

- Serve the frontend (static `dist/`) and run the backend API.
- Ensure the backend has write access to the SQLite path (or set `PLATEAUBREAKER_DB_PATH`).
- Configure `CORS_ORIGINS` for your deployed frontend domain(s).

### Deploying the frontend (SPA history mode)

The router uses HTML5 history mode (`createWebHistory`). Your static host must rewrite unknown routes to `index.html`,
otherwise refreshing `/analysis` or `/records` will 404.

Example (Nginx):

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

## Database migrations (backend)

This project includes a minimal Alembic setup under `backend/alembic/` for schema evolution.

**Rules of responsibility (important):**
- **New/blank environment** (no SQLite file yet, or the DB has no tables): the API server will bootstrap tables automatically on startup for convenience.
- **Existing environment** (DB already has tables): schema changes are **never** applied by the server; use **Alembic migrations**.
- **Production deployments**: run `alembic upgrade head` **before** starting the API server.
- `backend/data/` is only the default local storage location for SQLite. It is excluded from the release zip and is recreated at runtime as needed.

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt -c constraints.txt
alembic upgrade head
```

The server bootstrap (`create_db_and_tables`) only runs when the database is empty. It is not a migration system.
