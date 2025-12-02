# ⏳ Airflow Sensors 全面指南

**2025.10.22**

[Sensors](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/sensors.html) 是 Apache Airflow 中一類特殊的 **Operator**，用於「等待某條件滿足」後才繼續下游任務。例如等待檔案出現、資料庫有結果、API 回傳成功、或前序 DAG 完成。

---

## 🧩 一、Sensor 的核心概念

Sensor 本質上是 **延遲觸發（deferred execution）** 的 Operator。

它會在執行時進入「等待」狀態，並周期性地檢查條件是否成立。條件滿足時標記成功（`success`），否則持續 `poke`（探測），直到 timeout 或成功為止。

### 基本架構：

```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id="wait_for_input",
    filepath="/data/input/data_ready.csv",
    poke_interval=60,    # 每 60 秒檢查一次
    timeout=3600,        # 最多等待 1 小時
    mode="reschedule",  # 或 "poke"
)
```

**行為解釋：**

* `poke_interval`：感測間隔秒數。
* `timeout`：超時上限（秒）。
* `mode`：執行模式（poke/reschedule）。

---

## ⚙️ 二、Poke 模式 vs. Reschedule 模式

| 模式             | 說明                            | 優點         | 缺點                    |
| -------------- | ----------------------------- | ---------- | --------------------- |
| **poke**       | 任務持續佔用 worker，固定時間內不斷檢查條件     | 簡單、即時      | 會占用資源，對 long-wait 不友好 |
| **reschedule** | 每次 poke 後釋放 worker 資源，下次再排程檢查 | 節省資源、適合長等待 | 排程間隔稍長，非即時反應          |

> ✅ 實務建議：短等待（<5 分鐘）用 `poke`，長等待用 `reschedule`。

---

## 🧠 三、常見 Sensor 類型

### 1️⃣ FileSensor

等待檔案或資料夾出現：

```python
FileSensor(
    task_id="wait_csv",
    filepath="/tmp/input.csv",
    poke_interval=30,
)
```

### 2️⃣ ExternalTaskSensor

等待其他 DAG 或任務完成：

```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_prev_dag = ExternalTaskSensor(
    task_id="wait_prev_pipeline",
    external_dag_id="etl_daily",
    external_task_id="final_step",
    poke_interval=120,
)
```

### 3️⃣ S3KeySensor / GCSObjectExistenceSensor

等待雲端儲存檔案：

```python
S3KeySensor(
    task_id="wait_s3_upload",
    bucket_key="data/{{ ds }}/report.csv",
    bucket_name="my-bucket",
)
```

### 4️⃣ HttpSensor

等待 API 回應成功：

```python
HttpSensor(
    task_id="check_api",
    http_conn_id="weather_api",
    endpoint="/status",
    response_check=lambda r: r.json()['status'] == 'ok',
)
```

### 5️⃣ SqlSensor

等待 SQL 條件成立：

```python
SqlSensor(
    task_id="wait_data_ready",
    conn_id="postgres_conn",
    sql="SELECT COUNT(*) FROM data_table WHERE status='READY'",
    success=lambda count: count[0][0] > 0,
)
```

---

## 🧮 四、自訂 Sensor

可繼承 `BaseSensorOperator` 以自訂等待邏輯：

```python
from airflow.sensors.base import BaseSensorOperator

class MyCustomSensor(BaseSensorOperator):
    def poke(self, context):
        print("Checking condition...")
        return check_something()
```

`poke()` 方法需回傳 `True/False`：

* `True` → 條件成立 → success。
* `False` → 等待下一次 poke。

---

## 🕹️ 五、Sensor 的最佳實踐

✅ 建議：

* 長等待改用 `mode='reschedule'` 減少資源消耗。
* 設定合理 `timeout`，避免無限等待。
* 若多個 sensor 並行，考慮設置 `soft_fail=True` 允許非致命錯誤。
* 在 `poke()` 中加入 log 訊息，有助除錯。

⚠️ 避免：

* 在 Sensor 中進行長時間 I/O 操作。
* 無限等待（未設 timeout）。
* 在 poke 內重複開啟連線或大量讀寫。

---

## 🔍 六、Sensor 與 Trigger 機制（Airflow 2.5+）

新版 Airflow 支援 **Deferrable Sensors**，以 Trigger 替代傳統持續 poke。
這種設計可讓等待事件由 Trigger 進行（非占用 worker slot），效率大幅提升。

**範例：**

```python
from airflow.sensors.base import PokeReturnValue

class MyDeferrableSensor(BaseSensorOperator):
    def execute(self, context):
        self.defer(trigger=MyTrigger(...), method_name="resume_after")

    def resume_after(self, context, event=None):
        return event
```

**優點：**

* 不占用 worker slot。
* 支援更長期或非同步等待。
* 適合雲端或事件驅動工作流。

---

## 📘 七、總結

| 類別                 | 功能                    | 適用情境            |
| ------------------ | --------------------- | --------------- |
| FileSensor         | 等待本地或掛載路徑出現           | 檔案上傳、batch 完成   |
| ExternalTaskSensor | 等待其他 DAG/task 完成      | DAG 間依賴         |
| HttpSensor         | 等待 API 狀態或 webhook 回應 | 外部系統整合          |
| SqlSensor          | 等待資料庫條件成立             | ETL pipeline 檢查 |
| DeferrableSensor   | 非同步、事件觸發型             | 長期等待、高延遲任務      |

---

> ✅ **重點回顧**：Sensor 是「被動偵測」型任務，讓 Airflow 能與外部世界同步進度。合理使用 `mode`、`timeout` 與 Deferrable 機制，能顯著提升系統穩定性與資源效率。
