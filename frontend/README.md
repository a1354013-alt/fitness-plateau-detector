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

- This repo pins Node via `D:\\git\\plateau-breaker\\.nvmrc` (`20.19.0`).
- `package.json` also declares an `engines.node` range; use Node 20.19+ for consistent results.
- `frontend/.npmrc` sets `engine-strict=true`, so `npm ci` will fail fast if you use the wrong Node version (this is intentional for reproducibility).

If you want quieter install logs locally, you can run `npm ci --loglevel=error`.

## Why no `glob` deprecation warnings?

- Some upstream testing utilities pull in packages that depend on `glob`, which is deprecated on npm and prints noisy warnings.
- This repo avoids pulling `glob` into the dependency tree by overriding `js-beautify` with a tiny local shim at `vendor/js-beautify` (configured via `package.json` `overrides`).

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

## Notes

- `frontend/.npmrc` pins the npm cache to `frontend/.npm-cache` (helpful in restricted environments). The cache is safe to delete and is excluded from commits/releases.

## API base

- All requests use `baseURL: /api` in `src/services/api.ts`.
- In dev, Vite proxies `/api` to `http://localhost:8000`.

## State management (high level)

- `src/stores/healthRecords.ts`: server-side pagination query + delete-empty-page recovery
- `src/stores/analytics.ts`: split domain status for `dashboard` / `summary` / `trends` to avoid stale errors and cross-page coupling
