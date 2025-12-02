# Airflow Triggers

**2025.10.22**

本文介紹 Airflow 中的 **Triggers** 概念、使用場景與與傳統執行方式（Executor/Worker）的差異，並提供 SDK 風格範例示範如何在無需長時間佔用資源的情況下進行非同步任務處理。

---

## 🧩 一、Triggers 概念

**Trigger** 是 Airflow 2.2 引入的「非同步任務監聽機制」。

在傳統同步執行模式下（例如 `LocalExecutor` 或 `CeleryExecutor`），**Sensors** 會持續輪詢（polling）外部條件，例如等待檔案出現、API 回傳或 SQL 查詢結果。這種方法會佔用 worker slot，導致資源浪費。

為了解決此問題，Airflow 引入了 **Triggerer process** 與 **Deferrable Operators**，允許任務在等待條件時進入休眠狀態，僅在事件觸發時被喚醒。

> ✅ Trigger = Event-driven, Async, Non-blocking

---

## ⚙️ 二、運作機制

1. 當任務使用 **Deferrable Operator**（如 `DeferrableSensor`）時，會先註冊一個 **Trigger**（以 coroutine 型態執行）。
2. 該 Trigger 由獨立的 **Triggerer 進程** 執行，而非傳統 worker。
3. 當外部事件滿足條件（例如 API 回應、檔案出現），Triggerer 傳送事件回 scheduler。
4. Scheduler 將任務喚醒，任務恢復執行邏輯流程（通常從 deferral 點繼續）。

這樣可以顯著減少 idle 任務造成的資源浪費。

---

## 🧠 三、Trigger 與傳統 Executor/Worker 的比較

| 項目   | Executor/Worker        | Triggerer           |
| ---- | ---------------------- | ------------------- |
| 任務模式 | 同步（blocking）           | 非同步（async）          |
| 適用任務 | CPU-bound、I/O-bound 皆可 | 僅適用等待型任務（如 sensors） |
| 資源使用 | 持續佔用 worker slot       | 幾乎不佔用 slot          |
| 架構進程 | worker process         | triggerer process   |
| 實現方式 | Python thread/process  | asyncio coroutine   |

---

## 🧩 四、實作範例：Trigger + Sensor

以下範例展示如何以 `@dag` 搭配 `HttpSensorAsync` 使用非同步等待：

```python
from airflow.sdk import dag
from airflow.providers.http.sensors.http import HttpSensorAsync
from pendulum import datetime

@dag(
    dag_id="trigger_demo",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    description="Demonstrate Airflow Trigger and deferrable operator.",
    tags=["trigger", "sensor"]
)
def trigger_demo():
    """DAG 主體：展示非同步觸發機制。"""

    wait_api = HttpSensorAsync(
        task_id="wait_for_api",
        http_conn_id="my_api",
        endpoint="/status",
        poke_interval=60,
        timeout=600,
    )

    wait_api

trigger_demo()
```

**說明：**

* `HttpSensorAsync` 是非同步版本的 HTTP sensor。
* 當執行時，它會將等待邏輯交給 Triggerer，而不是佔用 worker。
* 當 API 回傳成功（200 OK）時，Triggerer 通知 scheduler，任務恢復執行。

---

## 🔧 五、Triggerer 設定與監控

### 啟動 Triggerer

在 Airflow CLI 或容器中執行：

```bash
airflow triggerer start
```

在 Docker Compose 環境中，通常已有對應服務，例如：

```yaml
triggerer:
  image: apache/airflow:latest
  command: triggerer
```

### 檢查狀態

```bash
airflow triggerer list
```

可列出目前註冊中的 triggers 與對應任務。

---

## 📈 六、常見使用情境

| 類型            | 範例                                    | 建議使用方式            |
| ------------- | ------------------------------------- | ----------------- |
| **等待 API 回應** | `HttpSensorAsync`                     | 使用非同步等待 REST 狀態變化 |
| **檔案監控**      | `S3KeySensorAsync`, `FileSensorAsync` | 等待雲端／本地檔案出現       |
| **資料庫查詢**     | `SqlSensorAsync`                      | 等待特定 SQL 條件成立     |
| **事件觸發任務**    | `TriggerDagRunOperator`               | 在事件到達後啟動下游 DAG    |

---

## 💡 七、最佳實踐

✅ **適合用 Trigger 的任務：**

* 需要等待外部條件（I/O bound）
* 等待時間較長（>5 分鐘）
* 不需持續運算的任務（如 sensors）

⚠️ **不建議使用的情況：**

* 即時計算或高頻查詢（短間隔 < 10 秒）
* CPU 密集或需多重同步流程的任務

---

## 📘 八、小結

Triggers 提供了一種 **事件驅動（event-driven）且非同步（async）** 的解法，使 Airflow 能在不佔用 worker 資源的前提下高效等待外部條件。對於長時間監控或等待型任務而言，Triggerer 是比傳統 Sensor 更現代且節能的選擇。
