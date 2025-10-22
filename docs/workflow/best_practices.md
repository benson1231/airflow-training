# Airflow DAG Best Practices

**2025.10.22**

---

## 🎯 目標
提供在設計與維護 Apache Airflow DAG 時的實務建議，幫助開發者撰寫 **可讀性高、可維護、可重現** 的工作流程。

---

## 🧩 1. DAG 結構設計

### ✅ 建議
- **一個 DAG 對應一個邏輯流程**，例如 ETL、報表生成或分析任務。
- DAG ID、task_id 命名需簡潔並具描述性，例如：`etl_daily_sales`、`load_to_bigquery`。
- 將 **重複任務模組化**，可封裝成 Python 函式或自訂 Operator。
- 將 **DAG 定義與任務邏輯分離**：
  - DAG 用於設定結構與排程。
  - 任務邏輯放在獨立模組中（例如 `tasks/transform.py`）。

### ⚠️ 避免
- 在 DAG 檔中直接寫大量業務邏輯或資料處理程式碼。
- 在 DAG 初始化階段讀取外部 API 或大型檔案（應放入 task 中）。

---

## ⏱️ 2. 排程與時間管理

### ✅ 建議
- 設定 `start_date` 並固定在 **過去時間**（避免非預期補跑）。
- 使用 `catchup=False` 避免不必要的歷史補執行（除非確實需要 backfill）。
- `schedule` 可用 cron 或 presets，例如：`@daily`、`@weekly`。
- 使用 `max_active_runs=1` 控制同時執行的 DAG Run 數量。

### ⚠️ 避免
- 將 `start_date` 設為動態時間（如 `datetime.now()`）。
- 不設定 `catchup` 導致意外觸發數百個歷史 DAG Run。

---

## 🔁 3. 任務撰寫與依賴設計

### ✅ 建議
- 使用 **TaskFlow API**（`@task` / `@task_group`）取代舊式 Operator 定義。
- 明確設定任務依賴：
  ```python
  extract() >> transform() >> load()
  ```
- 若任務之間需傳遞資料，使用 **XCom（自動）或外部儲存**。
- 設定合理的 `retries` 與 `retry_delay`，避免短時間重複失敗。

### ⚙️ 實例
```python
@dag(schedule='@daily', start_date=datetime(2024,1,1), catchup=False)
def etl_pipeline():

    @task(retries=2, retry_delay=timedelta(minutes=5))
    def extract():
        return get_data_from_api()

    @task()
    def transform(data):
        return clean_data(data)

    @task()
    def load(data):
        write_to_db(data)

    extract() >> transform() >> load()
```

---

## 📦 4. 變數與連線管理

### ✅ 建議
- 使用 Airflow **Variables** 或 **Connections** 管理環境設定。
- 機密資訊不應硬編碼在 DAG 檔中。
- 可結合 `.env` 或 Secrets Backend（Vault、AWS Secret Manager）。

### ⚙️ 範例
```python
from airflow.models import Variable
api_key = Variable.get("API_KEY")
```

---

## 📊 5. Logging 與監控

### ✅ 建議
- 利用 Airflow Web UI 檢視各任務 log。
- 設定 log rotation（避免長期堆積）。
- 整合 Slack / Email alert 通知錯誤：
  ```python
  default_args = {
      'email': ['team@domain.com'],
      'email_on_failure': True,
      'retries': 1
  }
  ```

---

## 🧪 6. 測試與開發流程

### ✅ 建議
- 本地開發可使用 `airflow dags test <dag_id>` 驗證 DAG 流程。
- 使用 `pytest` 搭配 `airflow.models.DAG` 進行單元測試。
- 確保 DAG 檔能在不連線外部服務的情況下載入（import 安全）。

---

## 🚀 7. 效能與維護

### ✅ 建議
- 定期清理舊任務與日誌 (`airflow db clean`)。
- 拆分大型 DAG 為多個小 DAG，並以 **TriggerDagRunOperator** 串接。
- 透過 **TaskGroup / Dynamic Task Mapping** 降低重複代碼。

---

## 📘 小結
| 面向 | 核心原則 |
|-------|------------|
| DAG 結構 | 單一職責、模組化、可重用 |
| 排程 | 固定 start_date、控制 catchup 與併發 |
| 任務 | 使用 TaskFlow API、明確依賴、設定 retries |
| 安全性 | 機密資料集中管理、不硬編碼 |
| 監控 | 使用 log、通知與 metrics |
| 測試 | 使用 airflow test 與 pytest 驗證 |
| 維運 | 清理資料、拆分大 DAG、動態任務生成 |

---

> 💡 **建議做法**：建立一個 `templates/` 或 `common_tasks/` 資料夾，用以儲存通用的任務模組、通知函式、錯誤處理邏輯，讓所有 DAG 都能共用相同標準，提升可維護性。