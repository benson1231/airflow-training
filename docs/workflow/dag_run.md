# Airflow DAG Runs

## 🧩 1. 概念總覽

在 Airflow 中，**DAG Run** 代表某一個 DAG 在特定時間點（或由使用者手動觸發）執行的「實例」。

每次執行一個 DAG（無論是自動排程還是手動觸發），都會產生一個新的 DAG Run，並包含所有任務（tasks）的狀態記錄、上下游依賴與執行結果。

> 簡言之：**DAG 是流程定義**，而 **DAG Run 是實際執行的記錄**。

---

## ⚙️ 2. DAG Run 的生成方式

### 🔹 自動排程（Scheduled Run）

當排程器（Scheduler）依據 `schedule_interval` 檢測到排程點時，會自動建立新的 DAG Run。

範例：

```python
@dag(
    schedule='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False
)
def my_dag():
    ...
```

若 `catchup=True`，當 DAG 啟用時，會自動補上過去尚未執行的排程點，形成多個 DAG Runs。

### 🔹 手動觸發（Manual Run）

由使用者透過 **UI** 或 **CLI** 手動建立，例如：

```bash
airflow dags trigger my_dag_id
```

手動建立的 DAG Run 沒有排程時間限制，可自由指定參數或日期。

### 🔹 外部觸發（External Trigger）

由其他 DAG 或外部系統透過 `TriggerDagRunOperator` 或 REST API 呼叫建立。例如：

```python
trigger = TriggerDagRunOperator(
    task_id='trigger_subdag',
    trigger_dag_id='sub_pipeline'
)
```

---

## 📅 3. DAG Run 的狀態（States）

| 狀態名稱           | 說明                     |
| -------------- | ---------------------- |
| `queued`       | 等待排程器觸發執行              |
| `running`      | 正在執行中                  |
| `success`      | 全部任務成功完成               |
| `failed`       | 至少一個任務失敗（未重試成功）        |
| `up_for_retry` | 有任務正在重試中               |
| `skipped`      | 所有任務被條件略過（如 Branching） |
| `manual`       | 由使用者手動建立的執行            |

---

## 🧠 4. Execution Date 與 Run ID

### 🧩 `execution_date`

代表該 DAG Run **對應的資料時間點**（而非實際執行時間）。

* 例如：每日排程的 2025-10-20 DAG Run 通常會在 2025-10-21 00:00 被建立。

### 🧩 `run_id`

Airflow 以唯一字串識別每個 DAG Run，格式範例：

* 自動排程：`scheduled__2025-10-20T00:00:00+00:00`
* 手動執行：`manual__2025-10-20T09:00:00+08:00`

兩者的關係如下：

```
DAG ID      → my_dag
execution_date → 2025-10-20
run_id         → scheduled__2025-10-20T00:00:00+00:00
```

---

## 📊 5. DAG Run 與 TaskInstance 關係

每個 DAG Run 會產生多個 **Task Instance**（任務實例），
每個任務實例記錄單一 task 在該 DAG Run 下的執行狀態。

例如：

```
DAG Run: scheduled__2025-10-20
 ├── task_a → success
 ├── task_b → running
 └── task_c → queued
```

透過這種層級結構，Airflow 能追蹤任務間的依賴、重試與整體流程狀態。

---

## 🔍 6. UI 觀察與管理

可在 Airflow Web UI 的 **Grid View / Graph View / Gantt View** 中觀察 DAG Run：

* **Grid View**：依時間排列 DAG Run，顯示各任務狀態。
* **Graph View**：以節點關係圖呈現 DAG 任務依賴。
* **Gantt View**：顯示任務執行時長與順序。
* **Code View**：查看對應版本的 DAG 原始碼。

---

## 🧩 7. 手動管理與 CLI 操作

### 查看所有 DAG Runs

```bash
airflow dags list-runs -d my_dag_id
```

### 觸發指定 DAG

```bash
airflow dags trigger my_dag_id --conf '{"key": "value"}'
```

### 清除特定任務或重新執行

```bash
airflow tasks clear my_dag_id --start-date 2025-10-18 --end-date 2025-10-20
```

---

## 💡 8. 最佳實踐

✅ **命名規則清晰**：run_id 應清楚標示日期與來源。
✅ **控制執行頻率**：利用 `max_active_runs` 限制同時運行數量。
✅ **善用參數化執行**：可在手動觸發時傳入 JSON 參數（`--conf`）。
✅ **監控與告警**：結合 Slack / Email Alert，追蹤每次 DAG Run 狀態。
✅ **清理歷史資料**：定期刪除舊 DAG Runs，以減輕 metadata DB 壓力。

---

> 🧭 **總結**：DAG Run 是 Airflow 的執行核心單位，連結了排程邏輯、任務執行、與資料時間。理解其生命週期能協助你更精準地控制工作流的再現性、調度與除錯。
