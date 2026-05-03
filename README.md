# Fitness Plateau Detector

**一個可解釋的體重停滯分析工具**

## 專案簡介

Fitness Plateau Detector 是一個旨在幫助使用者突破健身瓶頸的智能工具。它不僅僅是一個體重記錄應用，更是一個能夠**判斷資料品質、精準偵測體重停滯、深入分析潛在原因並提供個人化建議**的綜合性平台。我們的核心價值在於提供**可解釋的分析結果**，讓使用者清楚了解為何會遇到停滯，並獲得具體可行的改善方案。

## 核心價值與產品流程

傳統的體重追蹤工具往往只呈現數據，卻無法解釋數據背後的故事。Fitness Plateau Detector 填補了這一空白，透過以下核心產品流程，為使用者提供全面的健身洞察：

1.  **資料品質檢查 (Data Quality Check)**：確保輸入的體重、飲食、運動等數據的完整性與準確性，排除因資料缺失或異常造成的誤判。
2.  **體重停滯偵測 (Plateau Detection)**：運用先進演算法，精確識別體重下降趨勢中出現的停滯期，而非單純的短期波動。
3.  **原因分析 (Root Cause Analysis)**：深入探討導致停滯的多種潛在因素，例如卡路里攝取過高、睡眠不足、運動量減少、週末飲食失控等，並量化各因素的影響程度。
4.  **個人化建議 (Personalized Recommendations)**：根據分析結果，提供具體、可執行的改善建議，幫助使用者調整飲食、運動及生活習慣，有效突破停滯。
5.  **報告匯出 (Report Export)**：生成清晰易懂的週報，總結健身進度、分析結果與建議，方便使用者自我檢視或與教練溝通。

## 使用情境

*   **減脂與增肌**：個人化追蹤與分析，幫助使用者有效達成體態目標。
*   **健身紀錄**：系統化記錄每日健康數據，建立完整的健身歷程。
*   **教練輔助工具**：健身教練可利用本工具快速了解學員狀況，提供更精準的指導。
*   **作品集展示**：作為一個全端專案，展示開發者的技術實力與產品思維。

## 技術亮點

### Backend (FastAPI, SQLModel, Alembic, SQLite)

*   **高效能 API**：採用 FastAPI 框架，提供快速、非同步的 API 服務。
*   **資料模型與 ORM**：使用 SQLModel 結合 Pydantic 與 SQLAlchemy，實現資料模型定義、驗證與資料庫操作的無縫整合。
*   **資料庫遷移**：Alembic 用於管理資料庫 schema 變更，確保開發與部署過程中的資料一致性。
*   **資料庫約束**：利用 SQLite 的 DB-level CHECK constraints 確保資料完整性與業務邏輯的正確性。
*   **可解釋性分析**：後端實作了體重停滯偵測與原因分析的核心演算法，提供具體因素貢獻度與建議。

### Frontend (Vue 3, Vite, Pinia, PrimeVue)

*   **現代化前端框架**：基於 Vue 3 Composition API 開發，提供高效且響應式的使用者介面。
*   **快速開發體驗**：Vite 作為建構工具，提供極速的熱模組替換 (HMR) 與優化的打包性能。
*   **狀態管理**：Pinia 用於輕量級且直觀的狀態管理，確保應用程式數據流清晰可控。
*   **豐富 UI 組件**：PrimeVue 提供一套美觀且功能豐富的 UI 組件庫，加速介面開發並保持一致的設計風格。
*   **API 型別安全**：透過 `openapi-typescript` 從 OpenAPI 規範自動生成 API 客戶端型別，確保前後端介面的一致性與型別安全。

### Testing (Vitest, Playwright, Ruff, Mypy, Pytest)

*   **前端單元/組件測試**：Vitest 提供快速的測試運行器，結合 `@vue/test-utils` 進行 Vue 組件的單元測試。
*   **前端端到端測試**：Playwright 用於模擬使用者行為，進行跨瀏覽器的端到端測試，確保應用程式的整體功能與流程正確。
*   **後端程式碼品質**：Ruff 執行快速的 Python Linter，Mypy 進行靜態型別檢查，確保程式碼風格一致性與型別正確性。
*   **後端單元/整合測試**：Pytest 框架用於後端 API 與業務邏輯的測試，確保核心功能的穩定性。
*   **CI/CD 整合**：所有測試皆整合至 GitHub Actions CI 流程，確保每次程式碼提交都能自動驗證品質。

### Release & Deployment

*   **Docker 化部署**：提供 `Dockerfile` 與 `docker-compose.yml`，實現應用程式的容器化部署，簡化環境配置。
*   **API Contract 檢查**：CI 流程包含自動檢查 OpenAPI 規範與前端生成型別之間的差異，防止前後端介面不一致。
*   **版本同步檢查**：確保前後端版本號同步，便於版本管理與追溯。

## 作品集展示模式 (Demo Mode)

為了方便面試官快速體驗本專案的核心功能，我們提供了一鍵啟動的展示模式，其中預載了豐富的範例數據，包含體重、熱量、運動紀錄，以及一個典型的體重停滯案例，並展示其原因分析與建議。

### 快速啟動指南 (For Interviewers)

1.  **Clone 專案**：
    ```bash
    git clone https://github.com/a1354013-alt/fitness-plateau-detector
    cd fitness-plateau-detector
    ```
2.  **啟動 Docker 容器並載入 Demo 資料**：
    ```bash
    docker compose up --build -d
    # 等待服務啟動，然後執行 demo seed
    docker exec -it fitness-plateau-detector-backend-1 python backend/seed_data.py --scenario demo_plateau
    ```
    *注意：此指令會將 `demo_plateau` 情境的資料載入到 Docker 容器內的資料庫。* 
3.  **訪問應用程式**：
    打開瀏覽器，訪問 `http://localhost:8000`。您將看到預載了 demo 數據的儀表板、紀錄頁面和分析頁面。

### Demo 資料說明

*   **多週體重資料**：展示體重隨時間變化的趨勢。
*   **熱量與運動紀錄**：詳細記錄每日飲食攝取與運動消耗。
*   **體重停滯案例**：特別設計一個情境，清晰呈現體重停滯的發生，並在分析頁面提供其原因與建議。
*   **原因分析與建議**：在「Analysis」頁面，您將能看到系統如何解釋停滯原因（例如：週末高熱量攝取、睡眠不足等），並提供具體可行的改善建議。

### Demo 帳號

本專案目前不涉及使用者帳號系統，所有數據皆為匿名展示。您可以直接體驗所有功能。

## 已完成功能

*   使用者健康數據（體重、睡眠、卡路里、蛋白質、運動、步數、備註）的 CRUD 操作。
*   健康數據列表的分頁與篩選功能。
*   儀表板 (Dashboard) 顯示最新體重、7 日平均體重、睡眠、卡路里等關鍵指標。
*   體重趨勢圖與各項指標的歷史數據圖表。
*   體重停滯偵測與原因分析（卡路里超標、睡眠不足、週末過食、運動量減少、資料缺失等）。
*   基於分析結果的個人化行動建議。
*   週報匯出功能。
*   前後端分離架構，API 契約自動化檢查。
*   完整的單元測試、組件測試與端到端測試。
*   Docker 化部署。

## 未來擴充方向

*   **使用者認證與多使用者支援**：引入使用者註冊、登入功能，支援多個使用者獨立管理健康數據。
*   **更多數據整合**：整合來自穿戴裝置（如 Apple Health, Google Fit）的數據，自動化數據輸入。
*   **進階分析模型**：引入機器學習模型，提供更精準的停滯預測與個性化建議。
*   **目標設定與進度追蹤**：允許使用者設定體重、體脂、運動等目標，並可視化追蹤達成進度。
*   **社群互動功能**：增加使用者之間的互動、分享功能，形成社群支持。
*   **多語言支援**：提供多國語言介面，擴大應用範圍。
*   **行動應用程式**：開發原生 iOS/Android 行動應用，提供更流暢的使用體驗。

## Requirements

- Python: 3.11（CI 使用 3.11）
- Node: 20.19.0（由 repo root `.nvmrc` 固定；`frontend/.npmrc` 啟用 `engine-strict`）

## CI Parity: Local Verification (與 CI 一致的驗收命令)

以下命令對齊 `.github/workflows/ci.yml`；建議從 repo root 依序執行：

```bash
# contract
python scripts/check_version_sync.py
python scripts/check_api_contract.py

# backend
cd backend
ruff check .
mypy app/
pytest -q
alembic -c alembic.ini upgrade head

# frontend
cd ../frontend
npm ci
npm run lint
npm run test:ci
npm run build

# release packaging (smoke)
cd ..
python scripts/make_release_zip.py --out-dir release
python scripts/validate_release_zip.py --out-dir release

# integration smoke (backend serves built frontend)
python scripts/smoke_test_ci.py

# e2e (Playwright)
cd frontend
npx playwright install --with-deps
npx playwright test
```
