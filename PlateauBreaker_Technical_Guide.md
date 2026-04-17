# PlateauBreaker Technical Guide

此文件聚焦「資料契約 / 時間語義 / 規則引擎 / 部署與交付」的工程決策，讓作品在 code review 與面試講解時可直接引用。

## 1) Time Semantics（P0）

### `APP_TIMEZONE`：定義使用者視角的「今天」

- Env: `APP_TIMEZONE`（預設 `Asia/Taipei`）
- 單一來源：`backend/app/time.py`
  - `get_today()`：以 `APP_TIMEZONE` 計算 anchor date
  - 所有「today / 最近 N 天」都由此 helper（或 FastAPI dependency）提供

### Analytics 的 anchor date（避免 UTC 主機偏移）

- FastAPI dependency：`backend/app/dependencies/clock.py:get_anchor_date`
- `backend/app/api/analytics.py`
  - `/api/analytics/*` 端點統一透過 `Depends(get_anchor_date)` 取得 anchor date
- `backend/app/services/health_record_service.py:get_records_by_days`
  - 預設 anchor date 為 `get_today()`（不是 `date.today()`）

## 2) Data Contract（P0/P4）

### `record_date`（server-side 驗證）

- `backend/app/schemas/health_record.py`
  - Create / Update 都會拒絕未來日期（422）
  - 錯誤訊息包含最大允許日期：`record_date cannot be in the future (max: YYYY-MM-DD)`

### `created_at / updated_at`（UTC + `Z`）

- DB 欄位使用 `DateTime(timezone=True)`（見 `backend/app/models/health_record.py` + Alembic migration）
- API 輸出使用統一序列化：
  - `backend/app/time.py:format_datetime_utc_z`
  - `backend/app/schemas/health_record.py` 透過 `@field_serializer` 將輸出固定為 ISO 8601 UTC `Z`

### 輸入品質（避免髒資料污染分析）

在 `backend/app/schemas/health_record.py` 統一定義 create / update 規則：

- `note`：trim + 長度上限（`MAX_NOTE_LENGTH=500`），純空白視為 `null`
- `exercise_type`：trim + collapse whitespace
- `calories / protein / steps / exercise_minutes`：合理上限與 422 錯誤（避免極端值讓 KPI/圖表失真）

### DB 層防線（CHECK constraints）

僅靠 API 驗證不足以阻止「繞過 API 直接寫 DB」造成資料污染，因此在 Alembic migration 中加入可回滾的 CHECK constraints（`backend/alembic/versions/20260417_0003_health_record_checks.py`）：

- `weight`：`(0, 500]`
- `sleep_hours`：`[0, 24]`
- `calories`：`[0, 20000]`
- `protein`：`NULL` 或 `[0, 500]`
- `exercise_minutes`：`[0, 1440]`
- `steps`：`NULL` 或 `[0, 200000]`

## 3) Backend API（FastAPI）

Base URL: `/api`

### Meta / Health

- `GET /api/meta`：基本資訊（name/version/docs）
- `GET /health`：健康檢查（integration smoke 用）

### Health Records

- `GET /api/health-records?skip=&limit=&start_date=&end_date=`
  - 回傳 `{ total, records }`
  - records 依 `record_date` desc
- `POST /api/health-records`（201）
- `PUT /api/health-records/{record_id}`
  - 省略欄位：不更新
  - 對 non-nullable 欄位（`record_date/weight/sleep_hours/calories/exercise_minutes`）
    - 若 payload 明確送 `null`，會回 422（避免晚到 DB commit 才炸）
- `DELETE /api/health-records/{record_id}`（204）

### Analytics（Pydantic response models）

schema 定義於 `backend/app/schemas/analytics.py`

- `GET /api/analytics/dashboard`
  - KPI/平均：以「最近 7 個 **calendar days ending today**」為視窗
  - 平均值至少需要 5 天資料，否則平均欄位為 `null`
  - `weight_change_7d`：需要 **anchor date** 與 **anchor-7** 兩天都有資料才計算，否則 `null`
- `GET /api/analytics/trends?days=7..365`
- `GET /api/analytics/plateau`
- `GET /api/analytics/reasons?calorie_target=1000..5000`
- `GET /api/analytics/summary?calorie_target=1000..5000`

## 4) Rules Engine（可解釋、可測試）

### Plateau detection

檔案：`backend/app/rules/plateau_detector.py`

- 視窗：最近 7 個 calendar days（ending anchor date）
- 最少資料：`MIN_RECENT_DAYS=5`
- Rule A（趨勢變化）：last7 avg vs prev7 avg
- Rule B（波動帶）：(max-min) <= 0.6kg（等同 ±0.3kg band）

### Reasons analysis

檔案：`backend/app/rules/reason_analyzer.py`

回傳 top-2 + all reasons，並帶 diagnostic（missing days、data points）

## 5) Frontend Data Flow

- API client：`frontend/src/services/api.ts`
  - 型別來源：`frontend/src/generated/api.ts`
  - base URL：`VITE_API_BASE_URL`（若不設則用相對路徑，配合 dev proxy / same-origin 部署）
- Stores
  - `frontend/src/stores/analytics.ts`：dashboard + analysis state
  - `frontend/src/stores/healthRecords.ts`：records list + CRUD

## 6) API Contract Strategy（P1）

單一真相：backend OpenAPI（FastAPI/Pydantic schemas）

- export：`scripts/export_openapi.py`
- codegen：`openapi-typescript` → `frontend/src/generated/api.ts`
- drift check：`scripts/check_api_contract.py`（CI 必跑）

## 7) CI / Testing（P2）

Workflow：`.github/workflows/ci.yml`

- `contract`：OpenAPI → types drift 檢查
- `backend`：`ruff` + `alembic upgrade head` smoke + `pytest --cov` gate
- `frontend`：`eslint` + `vitest` coverage fail-under gate（`npm run test:ci`）+ `vite build` + release packaging smoke
- `integration`：啟動 backend、驗證主要 API、驗證 backend 提供 SPA 靜態檔與 history fallback，並確保 `/api/*` 不被 fallback 汙染（`scripts/smoke_test_ci.py`）

## 8) Delivery（P3）

### Docker / Compose

- `Dockerfile`：multi-stage（build 前端 → python runtime）
  - container 啟動會先 `alembic upgrade head` 再啟動 `uvicorn`
- `docker-compose.yml`：一鍵 demo（DB volume: `./data`）

### Release zip

- `scripts/make_release_zip.py`：產生乾淨可交付 zip（排除 tests/cache/db/node_modules）
- `scripts/validate_release_zip.py`：驗證 zip 內容符合交付標準
