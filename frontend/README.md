# PlateauBreaker Frontend

This folder contains the PlateauBreaker Vue 3 + Vite frontend.

For the full project overview, backend setup, and packaging instructions, see the repository root `README.md`.

## Local development

```powershell
cd frontend
npm ci
npm run dev
```

The dev server proxies `/api` to the backend (see `vite.config.ts`).

## Production build

```powershell
cd frontend
npm ci
npm run build
```
