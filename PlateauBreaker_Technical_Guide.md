# PlateauBreaker Technical Guide

## Backend API (FastAPI)

Base URL: `/api`

### Health records

- `GET /health-records?skip=&limit=&start_date=&end_date=`
  - Returns `{ total, records }`
  - Records are ordered by `record_date` desc
- `POST /health-records`
- `PUT /health-records/{id}`
- `DELETE /health-records/{id}`

### Analytics (formal response models)

All endpoints under `/analytics/*` have explicit Pydantic response models defined in `backend/app/schemas/analytics.py`.

- `GET /analytics/dashboard`
  - 7-day averages are based on the **last 7 calendar days ending today** (requires at least 5 recorded days; otherwise the average fields are `null`)
  - `current_weight` is the latest recorded weight (see `last_record_date`)
  - `weight_change_7d` is **today's weight minus the weight on the exact date 7 days ago**; if either date is missing, it is `null`

- `GET /analytics/trends?days=7..365`
  - Time-series data for charts

- `GET /analytics/plateau`
  - Plateau detection result (rule outputs + metrics)

- `GET /analytics/reasons?calorie_target=1000..5000`
  - Ranked reason codes (top-2) + diagnostics

- `GET /analytics/summary?calorie_target=1000..5000`
  - Combined response `{ plateau, reasons, summary }`
  - `summary` payload uses stable keys: `text`, `insight`, `status`, `top_reasons`

## Plateau detection (rules)

Evaluated on the last 7-day window (calendar days) ending **today**.

- Minimum data requirement: **at least 5 recent days** of records
- Rule A (trend change): compare the last 7-day average vs the previous 7-day average
  - Plateau condition: `abs(avg_change) < 0.2 kg`
- Rule B (fluctuation band): within the last 7 days
  - Plateau condition: `(max - min) <= 0.6 kg` (equivalent to ±0.3 kg)

## Reason analysis (top factors)

Evaluated on the last 7-day window (calendar days) ending **today**.

- Minimum data requirement: **at least 5 recent days** of records
- Returns top-2 reasons by severity

Reason codes:
- `SleepIssue`
- `CalorieIssue`
- `WeekendOvereating`
- `ExerciseDrop`
- `DataMissing`

## Frontend data flow

- `frontend/src/services/api.ts` is the single source of truth for API contracts used by stores/views
- `frontend/src/stores/analytics.ts` is the single source of truth for dashboard/analysis state
- `frontend/src/stores/healthRecords.ts` owns record pagination query state and handles delete-empty-page recovery
- `frontend/src/components/StatePanel.vue` standardizes loading/error/empty presentation across pages
