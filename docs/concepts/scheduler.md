# Airflow Scheduler 運作原理完整指南

**2025.10.22**

Airflow 的 [Scheduler](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html) 是整個工作流程的「排程大腦」，負責根據 DAG 的設定，自動建立 DAG Run、產生任務執行排程，並將任務交給 Executor 執行。了解 Scheduler 的運作機制，有助於掌握 Airflow 為何、何時觸發任務。

---

## 🧩 一、Scheduler 的角色定位

在 Airflow 架構中：

```
DAG 定義（schedule, start_date, catchup）
          ↓
     Scheduler → 產生 DAG Run（execution_date）
          ↓
     Executor → 分派任務到 Worker 執行
```

| 元件            | 功能                             |
| ------------- | ------------------------------ |
| **Scheduler** | 根據 DAG 規則決定哪些任務該執行、何時執行        |
| **Executor**  | 負責將任務分配到執行環境（本地、Celery、K8s...） |
| **Worker**    | 實際執行任務（Python、Bash、SQL 等）      |

簡而言之：

> Scheduler 負責「決策與排程」，Executor 負責「執行與派發」。

---

## 🕓 二、Scheduler 的運作流程

Scheduler 是一個常駐的守護進程（daemon process），會週期性地執行以下步驟：

```
1️⃣ 掃描 DAG 資料夾中的所有 DAG 定義檔
2️⃣ 解析 DAG 的 schedule/start_date/catchup 等設定
3️⃣ 檢查 Metadata DB 中的現有 DAG Run 狀態
4️⃣ 判斷哪些排程週期尚未建立 DAG Run
5️⃣ 產生新的 DAG Run（execution_date）記錄
6️⃣ 對應每個任務建立 TaskInstance 並送交 Executor
```

運作示意圖：

```
+-------------------------+
|        Scheduler        |
|-------------------------|
| DAG 掃描與排程分析      |
| 建立 DAG Run            |
| 建立 TaskInstance        |
| 通知 Executor 分派任務  |
+-------------------------+
```

---

## 🧮 三、Scheduler 與排程參數的關係

Scheduler 根據以下關鍵屬性運作：

| 屬性                               | 來源       | 功能                    |
| -------------------------------- | -------- | --------------------- |
| `start_date`                     | DAG 層設定  | 第一個排程週期的起始點           |
| `schedule` / `schedule_interval` | DAG 層設定  | 決定週期性（cron / @preset） |
| `catchup`                        | DAG 層設定  | 是否補跑過去未執行的週期          |
| `max_active_runs`                | DAG 層設定  | 限制同時進行的 DAG Run 數量    |
| `depends_on_past`                | Task 層設定 | 是否依賴前一個週期的結果          |

Scheduler 每次啟動都會根據這些屬性比對資料庫中的記錄，判斷哪些週期需要新建 DAG Run。

---

## 🧠 四、DAG Run 產生邏輯

舉例：

```python
@dag(
    dag_id="daily_report",
    start_date=datetime(2025, 10, 1),
    schedule="@daily",
    catchup=True,
)
def daily_report():
    ...
```

* 第一個 `execution_date` 為 `2025-10-01`
* Scheduler 在 `2025-10-02 00:00` 觸發執行
* 若中間關閉數天，重啟後會補跑（catchup=True）

---

## ⚙️ 五、Scheduler 與 Executor 的互動

1. Scheduler 建立 `TaskInstance` 物件並存入 Metadata DB。
2. Scheduler 將待執行任務送給 Executor。
3. Executor 決定任務的執行環境（Local / Celery / K8s）。
4. Worker 實際執行任務，回報結果至 Metadata DB。

互動流程：

```
Scheduler → Executor → Worker → Metadata DB
      ↑                            ↓
      └─────── 狀態更新 / 任務回報 ───────┘
```

---

## 📦 六、Scheduler 的設定與啟動

### 啟動 Scheduler：

```bash
airflow scheduler
```

### 關鍵設定（airflow.cfg）：

```ini
[scheduler]
max_threads = 2            # Scheduler 併發任務處理數
scheduler_heartbeat_sec = 5  # 心跳間隔（秒）
min_file_process_interval = 30  # DAG 檔重新解析間隔（秒）
```

### 檢查狀態：

```bash
ps aux | grep airflow
# 或使用 web UI 的 Scheduler 標籤檢查運作狀況
```

---

## 🔍 七、Scheduler 的常見問題與排錯

| 問題               | 可能原因                           | 解法                                           |
| ---------------- | ------------------------------ | -------------------------------------------- |
| DAG 沒有被觸發        | Scheduler 未啟動 / start_date 在未來 | 啟動 Scheduler 或調整 start_date                  |
| 任務卡在 "queued" 狀態 | Executor 未啟動或連線失敗              | 檢查 Executor 配置與 Broker 狀態                    |
| DAG 未更新          | DAG 檔未重新載入                     | 調整 `min_file_process_interval` 或重啟 Scheduler |
| Scheduler 負載過高   | 任務太多 / 週期太短                    | 提升 `max_threads` 或改用分散式 Executor             |

---

## 🧮 八、Scheduler 與 Catchup / Backfill 的差異

| 機制         | 負責元件      | 功能          | 執行方式                                  |
| ---------- | --------- | ----------- | ------------------------------------- |
| `catchup`  | Scheduler | 啟動時自動補跑過去週期 | 自動建立歷史 DAG Run                        |
| `backfill` | CLI       | 手動指定補跑時間範圍  | `airflow dags backfill -s ... -e ...` |

---

## 💡 九、最佳實踐建議

✅ 建議：

* 生產環境使用 **LocalExecutor 或 CeleryExecutor** 搭配獨立 Scheduler 節點。
* 將 Scheduler 與 Worker 分開部署，避免資源爭奪。
* 設定 `max_active_runs` 控制同時執行的 DAG Run 數量。
* 在多 DAG 環境中適度調整 `scheduler_heartbeat_sec`、`max_threads`。

⚠️ 避免：

* 在 SQLite（SequentialExecutor）環境長期使用 Scheduler。
* DAG 檔案過多且週期極短，容易造成 Scheduler 掃描延遲。

---

## 🧭 十、總覽圖（Scheduler 全流程）

```
       +-----------------------------+
       |          Scheduler          |
       |-----------------------------|
       | DAG 掃描 → 產生 DAG Run → 任務分派 |
       +-----------------------------+
                    |
                    v
       +-----------------------------+
       |          Executor           |
       | 決定執行環境（本地/Celery/K8s） |
       +-----------------------------+
                    |
                    v
       +-----------------------------+
       |           Worker            |
       | 執行實際任務，回報結果至 DB     |
       +-----------------------------+
```

---

> ✅ **結論：** Scheduler 是 Airflow 的核心排程引擎，負責根據 DAG 設定建立執行週期並分派任務。掌握 Scheduler 的邏輯，有助於理解 DAG 為何未觸發、如何補跑、以及任務如何流向 Executor 與 Worker。
