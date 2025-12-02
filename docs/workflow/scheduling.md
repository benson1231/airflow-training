# Airflow Scheduling

**2025.10.20**

本文整理 Airflow 的排程（Scheduling）核心觀念與機制，包括 DAG 時間邏輯、`catchup`、`backfill`、觸發行為、以及與任務排程相關的進階參數設定。

---

## 🧭 一、排程的基本概念

在 Airflow 中，**DAG（Directed Acyclic Graph）** 定義了一組有依賴關係的任務與其執行頻率。排程行為由以下三個要素決定：

1. **`start_date`** — DAG 開始執行的基準時間。
2. **`schedule` / `schedule_interval`** — 指定週期，例如每日、每小時或自訂 CRON 表達式。
3. **`catchup`** — 是否補跑過去未執行的排程週期。

### ⏰ DAG Run 的排程邏輯

每個 DAG Run 代表某個排程週期的執行實例。Airflow 的排程邏輯如下：

> 一個 DAG Run 的 `execution_date` 代表**該週期開始的時間點**，而實際執行通常在該週期「結束時刻」觸發。

例如：

* `schedule="@daily"` 且 `start_date=2025-10-01`，則第一個 DAG Run（execution_date=2025-10-01）會在 **2025-10-02 00:00** 被觸發。

這種「延後觸發」是 Airflow 的標準行為，用於確保當日資料完整可用後再執行分析任務。

---

## 🧩 二、`catchup` — DAG 層級自動補跑

**定義**：
`catchup` 控制當 DAG 第一次啟用或系統重新啟動時，是否要自動補上過去未執行的週期。

**範例：**

```python
@dag(
    dag_id="example_dag",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,   # 👈 不補跑過去的
)
def example_dag():
    ...
```

| 參數值                | 行為                                    |
| ------------------ | ------------------------------------- |
| `catchup=True`（預設） | 會從 `start_date` 開始，依序補跑至目前日期前一日的所有週期。 |
| `catchup=False`    | 只會執行最新一次排程，不補舊週期。                     |

**使用時機：**

* 生產環境常設為 `False`，避免啟用時大量任務堆積。
* 初次建置或需要完整補資料時，暫時開啟 `True`。

---

## 🕓 三、`backfill` — CLI 手動補跑

`backfill` 是 CLI 命令，可手動指定時間範圍回補執行，無視 `catchup` 設定。

```bash
airflow dags backfill -s 2025-10-01 -e 2025-10-05 my_dag_id
```

| 參數                   | 說明                    |
| -------------------- | --------------------- |
| `-s`, `--start-date` | 補跑開始日期                |
| `-e`, `--end-date`   | 補跑結束日期                |
| `--reset-dagruns`    | 刪除該區間的舊 DAG Run 後重新執行 |
| `--mark-success`     | 只標記成功，不執行任務           |

**使用場景：**

* 歷史資料補算或重建特定日期資料。
* DAG 結構變動後，需要重跑過去特定區段。

---

## 🧮 四、排程相關參數與控制項

| 參數                               | 用途                 | 範例                            |
| -------------------------------- | ------------------ | ----------------------------- |
| `start_date`                     | 第一個排程週期的基準時間       | `datetime(2025,1,1)`          |
| `end_date`                       | 排程的結束時間（可選）        | `datetime(2025,12,31)`        |
| `schedule` / `schedule_interval` | 排程週期，可用 CRON 或簡寫   | `"@daily"`, `"0 6 * * *"`     |
| `catchup`                        | 是否自動補跑             | `True` / `False`              |
| `max_active_runs`                | 限制同時進行的 DAG Run 數量 | `max_active_runs=1`           |
| `depends_on_past`                | 任務是否需依賴前一次成功執行     | `True` / `False`              |
| `retries`                        | 任務失敗重試次數           | `default_args={"retries": 2}` |
| `retry_delay`                    | 每次重試間隔             | `timedelta(minutes=5)`        |

---

## 🧠 五、觸發模式與運行方式

Airflow DAG 可透過三種方式被觸發：

1. **自動排程（Scheduler）** — 根據 `schedule` 規則由排程器觸發。
2. **手動觸發（Manual Trigger）** — 由使用者在 UI 或 CLI 手動執行：

   ```bash
   airflow dags trigger my_dag_id
   ```
3. **外部觸發（External Trigger）** — 由其他 DAG 或 API 觸發，例如 `TriggerDagRunOperator`。

---

## 🔍 六、常見時間陷阱與排錯建議

| 問題         | 原因                                           | 解法                    |
| ---------- | -------------------------------------------- | --------------------- |
| DAG 沒有自動執行 | `start_date` 在未來時間、或 `catchup=False` 導致沒有排程點 | 調整 `start_date` 或手動觸發 |
| 補跑未生效      | DAG Run 已存在，未加 `--reset-dagruns`             | 加上參數重新執行              |
| 排程提早或延遲    | 誤解 execution_date 與觸發時間差一日                   | 確認排程邏輯與時區設定           |

---

## 💡 七、實務建議

* **Production 環境**：`catchup=False` + `max_active_runs=1`，確保穩定與可控。
* **資料補算任務**：使用 `backfill`，靈活補跑歷史區間。
* **開發測試環境**：可用 `schedule=None`，僅手動觸發。
* **注意時區**：建議統一使用 `pendulum.timezone("Asia/Taipei")` 控制時間一致性。

---

> ✅ 小結：Airflow 的排程行為取決於 DAG 的時間參數設計與 Scheduler 的觸發邏輯。善用 `catchup` 與 `backfill` 可精準控制歷史資料的補算與日常自動排程。
