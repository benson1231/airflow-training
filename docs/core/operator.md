# Airflow Operator 完整指南

在 Apache Airflow 中，[`Operator`](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html) 是建立任務（task）的核心元件。每個 Operator 代表一個具體的動作，例如執行 Python 函式、運行 Bash 指令、呼叫 API、觸發其他 DAG 等。熟悉 Operator 是撰寫 DAG 的基礎之一。

---

## 🧩 一、Operator 的角色

在 DAG（Directed Acyclic Graph）中：

* 每個 **節點 (Node)** 是一個 Operator 實例。
* 每個 **邊 (Edge)** 表示任務的依賴關係。

簡單理解：

> **DAG 定義流程邏輯，Operator 定義具體任務行為。**

範例：

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello():
    print("Hello, Airflow!")

dag = DAG(
    dag_id="operator_demo",
    start_date=datetime(2025,1,1),
    schedule="@daily",
    catchup=False,
)

say_hello = PythonOperator(
    task_id="say_hello",
    python_callable=hello,
    dag=dag,
)
```

---

## ⚙️ 二、Operator 的主要類別

Airflow 內建的 Operator 可分為幾大類：

### 1️⃣ **Base Operators（核心通用型）**

| 類別                                 | 說明                          |
| ---------------------------------- | --------------------------- |
| `PythonOperator`                   | 執行 Python 函式，最常用的 Operator。 |
| `BashOperator`                     | 執行 Shell / Bash 指令。         |
| `BranchPythonOperator`             | 用 Python 邏輯控制流程分支。          |
| `DummyOperator`（或 `EmptyOperator`） | 佔位用，不執行實際任務。                |
| `ShortCircuitOperator`             | 依條件決定是否繼續執行下游任務。            |

---

### 2️⃣ **External / Trigger Operators（控制 DAG / 任務觸發）**

| 類別                      | 說明                    |
| ----------------------- | --------------------- |
| `TriggerDagRunOperator` | 觸發另一個 DAG 執行。         |
| `ExternalTaskSensor`    | 等待另一個 DAG / 任務完成後再繼續。 |
| `LatestOnlyOperator`    | 只在最新一次排程時執行，跳過舊週期。    |

---

### 3️⃣ **Sensors（等待條件達成）**

[詳細介紹](./sensor.md)

| 類別            | 說明                   |
| ------------- | -------------------- |
| `S3KeySensor` | 等待特定檔案出現在 S3 bucket。 |
| `HttpSensor`  | 等待 HTTP 端點回應成功。      |
| `SqlSensor`   | 等待 SQL 查詢結果符合條件。     |
| `FileSensor`  | 等待本地或遠端檔案存在。         |

Sensors 皆繼承自 `BaseSensorOperator`，常見參數：

```python
poke_interval=60  # 每 60 秒檢查一次
mode='reschedule' # 省資源模式（建議）
```

---

### 4️⃣ **Transfer Operators（資料搬移）**

| 類別                      | 說明                                  |
| ----------------------- | ----------------------------------- |
| `S3ToGCSOperator`       | 從 AWS S3 傳資料到 Google Cloud Storage。 |
| `GCSToBigQueryOperator` | 將 GCS 中的資料匯入 BigQuery。              |
| `S3ToRedshiftOperator`  | 從 S3 匯入 Redshift。                   |

Transfer Operators 常用於 ETL / 資料管線的中繼階段。

---

### 5️⃣ **SQL / Database Operators**

| 類別                  | 說明                   |
| ------------------- | -------------------- |
| `PostgresOperator`  | 執行 PostgreSQL 指令。    |
| `BigQueryOperator`  | 執行 BigQuery SQL 查詢。  |
| `SnowflakeOperator` | 執行 Snowflake SQL 查詢。 |
| `MySqlOperator`     | 執行 MySQL 指令。         |

大多數資料庫類 Operator 都接受 `sql` 參數，可放入查詢字串或 `.sql` 檔案路徑。

---

### 6️⃣ **Email / Notification Operators**

| 類別                     | 說明                           |
| ---------------------- | ---------------------------- |
| `EmailOperator`        | 寄送電子郵件通知。                    |
| `SlackAPIPostOperator` | 發送 Slack 訊息。                 |
| `HttpOperator`         | 呼叫 HTTP API（常用於 webhook 通知）。 |

---

### 7️⃣ **Custom Operators（自訂 Operator）**

若內建的類別無法滿足需求，可繼承 `BaseOperator` 自行擴充。

範例：

```python
from airflow.models import BaseOperator

class CustomPrintOperator(BaseOperator):
    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def execute(self, context):
        print(f"[CustomPrintOperator] {self.message}")
```

使用：

```python
custom_task = CustomPrintOperator(
    task_id='custom_message',
    message='Hello from custom operator!',
    dag=dag,
)
```

---

## 🔁 三、Operator 之間的依賴設定

Operator 之間可用以下方式設定上下游關係：

```python
# 傳統方式
extract_task.set_downstream(transform_task)
transform_task.set_upstream(load_task)

# 簡潔運算子語法
extract_task >> transform_task >> load_task
# 或
load_task << transform_task << extract_task
```

---

## 🧠 四、Operator 共用參數（BaseOperator Arguments）

| 參數                 | 說明                              | 範例                              |
| ------------------ | ------------------------------- | ------------------------------- |
| `task_id`          | 任務名稱（唯一）                        | `'extract_data'`                |
| `retries`          | 失敗重試次數                          | `retries=3`                     |
| `retry_delay`      | 重試間隔時間                          | `timedelta(minutes=5)`          |
| `depends_on_past`  | 是否依賴前次成功                        | `True / False`                  |
| `email_on_failure` | 任務失敗時寄信                         | `True`                          |
| `sla`              | 任務完成期限（Service Level Agreement） | `timedelta(hours=1)`            |
| `trigger_rule`     | 控制下游任務觸發條件                      | `'all_success'`, `'one_failed'` |

---

## ⚙️ 五、Trigger Rules（觸發規則）

| 規則                | 行為                |
| ----------------- | ----------------- |
| `all_success`（預設） | 所有上游成功才執行         |
| `all_failed`      | 所有上游失敗才執行         |
| `one_success`     | 任一上游成功就執行         |
| `one_failed`      | 任一上游失敗就執行         |
| `none_failed`     | 無上游失敗即執行（包含 skip） |
| `always`          | 不論結果都執行（例如清理任務）   |

範例：

```python
cleanup = PythonOperator(
    task_id='cleanup',
    python_callable=clean_temp,
    trigger_rule='always',
    dag=dag,
)
```

---

## 📦 六、Operator vs Sensor vs TaskFlow API

| 類型                         | 說明                 | 適合情境                 |
| -------------------------- | ------------------ | -------------------- |
| **Operator**               | 一般任務執行單元           | 執行函式、SQL、API、系統命令    |
| **Sensor**                 | 特殊 Operator，用於等待條件 | 等待資料、外部事件、檔案出現       |
| **TaskFlow API (`@task`)** | 以函式形式建立任務，語法更簡潔    | Python native DAG 寫法 |

---

## 💡 七、實務建議

✅ 建議：

* 任務粒度要適中，避免單一 Operator 包含過多邏輯。
* 若任務之間需交換資料，用 XCom 傳遞小型結果。
* 將常用自訂邏輯包裝成 Custom Operator，提高可重用性。

⚠️ 避免：

* 在 BashOperator 中執行複雜業務邏輯（應轉為 PythonOperator）。
* 在 DAG 裡直接使用大量外部連線（應以 Hook 管理連線）。

---

> ✅ **總結：** Operator 是 Airflow 任務的核心單位。熟悉內建 Operator 類別、Trigger Rule 與自訂擴充方式，能讓整個工作流程模組化、可維護、可觀測。
