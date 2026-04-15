# PlateauBreaker Frontend

This folder contains the PlateauBreaker Vue 3 + Vite frontend.

For the full project overview, backend setup, and packaging instructions, see the repository root `README.md`.

## What this frontend does

- Provides 3 pages: Dashboard, Records, Analysis
- Uses `Pinia` stores to own query/state and keep page logic predictable
- Calls the backend API via `src/services/api.ts` (single source of truth for contracts)

## Local development

```powershell
cd frontend
npm ci
npm run dev
```

The dev server proxies `/api` to the backend (see `vite.config.ts`).

## Node version (required)

- This repo pins Node via `.nvmrc` (`20.19.0`) at the repository root.
- `package.json` also declares an `engines.node` range; use Node 20.19+ for consistent results.
- `frontend/.npmrc` sets `engine-strict=true`, so `npm ci` will fail fast if you use the wrong Node version (this is intentional for reproducibility).

If you want quieter install logs locally, you can run `npm ci --loglevel=error`.

## Deprecation warnings (upstream)

- Some upstream packages used for testing may emit `deprecated` warnings during install.
- This repo does not patch/fork upstream dependencies in the final-ready baseline; CI runs installs with `--loglevel=error` to keep logs clean and focus on failures.

## Production build

```powershell
cd frontend
npm ci
npm run build
```

## Tests

```powershell
cd frontend
npm ci
npm test
```

## CI note

- The repository CI does more than frontend test/build:
  - frontend `npm ci`
  - frontend `npm run lint`
  - frontend `npm test -- --run`
  - frontend `npm run build`
  - release packaging smoke test via `scripts/make_release_zip.py` + `scripts/validate_release_zip.py`
- Backend tests and migration/release rules are documented in the root `README.md`.

## Notes

- `frontend/.npmrc` pins the npm cache to `frontend/.npm-cache` (helpful in restricted environments). The cache is safe to delete and is excluded from commits/releases.

## API base

- `src/services/api.ts` resolves the API base URL in this order:
  - `VITE_API_BASE_URL` (if set)
  - fallback `/api` (keeps Vite dev proxy working)
- In dev, Vite proxies `/api` to `http://localhost:8000` (see `vite.config.ts`).
- In production (or when not using the proxy), copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL`.
  - Reminder: Vite env vars are **build-time**; restart `npm run dev` or rebuild after changes.

## State management (high level)

- `src/stores/healthRecords.ts`: server-side pagination query + delete-empty-page recovery
- `src/stores/analytics.ts`: split domain status for `dashboard` / `summary` / `trends` to avoid stale errors and cross-page coupling
