# Airflow Worker 運作原理與角色說明

**2025.10.22**

Airflow 的 **Worker** 是實際執行任務（Task）的核心元件。Scheduler 負責排程任務，Executor 負責分配任務，而 Worker 則負責真正「跑起來」每一個任務邏輯。理解 Worker 的運作模式，是掌握任務執行效能與穩定性的關鍵。

---

## 🧩 一、Worker 的角色定位

整體架構可簡化為：

```
DAG → Scheduler → Executor → Worker → Task 執行
```

| 元件            | 功能                           |
| ------------- | ---------------------------- |
| **Scheduler** | 決定任務該何時執行                    |
| **Executor**  | 分派任務給 Worker                 |
| **Worker**    | 實際執行任務邏輯（Python、Bash、SQL...） |

在 Airflow 中，每個任務實例（TaskInstance）最終都會在一個 Worker 進程上被執行。

---

## ⚙️ 二、Worker 的運作流程

1️⃣ **Executor 接收到任務排程指令**
由 Scheduler 建立的任務（TaskInstance）會被送入 Executor 的佇列。

2️⃣ **Executor 將任務分派給可用 Worker**
依照使用的 Executor 類型（Local、Celery、Kubernetes...）決定任務的執行位置。

3️⃣ **Worker 啟動任務執行環境**
Worker 會：

* 建立臨時執行環境（Process 或 Pod）
* 載入 DAG code 與任務上下文（context）
* 執行 `task.execute()` 內部邏輯

4️⃣ **Worker 回報任務結果**
任務完成或失敗後，Worker 會更新 Metadata Database 中的狀態：

* `success`
* `failed`
* `up_for_retry`

---

## 🧮 三、不同 Executor 下的 Worker 行為

| Executor 類型                  | Worker 運作模式                             | 適用情境   |
| ---------------------------- | --------------------------------------- | ------ |
| **LocalExecutor**            | Worker 由同機多進程組成（multiprocessing）        | 單機多核部署 |
| **CeleryExecutor**           | Worker 為獨立節點，由 Celery 啟動，透過 Broker 接收任務 | 分散式環境  |
| **KubernetesExecutor**       | 每個任務自動產生一個獨立 Pod 作為 Worker              | 雲原生部署  |
| **CeleryKubernetesExecutor** | 混合模式，可由 Celery 或 K8s 執行任務               | 企業級架構  |

### 💡 Celery Worker 範例

CeleryExecutor 會啟動多個 Worker 節點，每個節點可獨立接收任務：

```bash
airflow celery worker
```

Celery Broker（Redis / RabbitMQ）負責將任務派送給可用 Worker。

---

## 🔧 四、Worker 的關鍵設定

在 `airflow.cfg` 中可以設定 Worker 的行為：

```ini
[celery]
worker_concurrency = 8        # 單個 Worker 同時執行任務數
worker_prefetch_multiplier = 1  # 每次抓取任務數量
worker_autoscale = 16,4       # 最大 / 最小並行數

[core]
parallelism = 32              # 全系統最大併行任務數
```

KubernetesExecutor 下則可在 Helm 或 values.yaml 指定：

```yaml
workers:
  replicas: 4
  resources:
    limits:
      cpu: 1
      memory: 1Gi
```

---

## 🧠 五、Worker 的生命週期

```
+-----------------------------+
|         Scheduler           |
+-------------+---------------+
              |
              v
+-------------+---------------+
|          Executor            |
+-------------+---------------+
              |
              v
+-------------+---------------+
|            Worker            |
|-----------------------------|
| 1. 接收任務 → 2. 執行邏輯 → 3. 回報狀態 |
+-----------------------------+
```

---

## 📦 六、Worker 的日誌與監控

每個 Worker 都會在本地或遠端（如 S3, GCS）保存任務日誌。

查看任務日誌：

```bash
airflow tasks logs <dag_id> <task_id> <execution_date>
```

或在 Web UI → **DAGs → Task Instance → Log** 查看。

Celery 環境中也可監控 Worker 狀態：

```bash
airflow celery status
# 或直接查看 celery process
ps aux | grep celery
```

---

## 🔍 七、常見問題與排錯

| 問題            | 可能原因                    | 解法                                 |
| ------------- | ----------------------- | ---------------------------------- |
| 任務卡在 `queued` | Worker 未啟動或無法連線至 Broker | 檢查 Celery Broker（Redis / RabbitMQ） |
| 任務失敗無重試       | 任務定義未設 `retries`        | 加入 `retries` 與 `retry_delay` 參數    |
| Worker CPU 過載 | `worker_concurrency` 太高 | 降低並行數或擴充 Worker 節點                 |
| 任務日誌缺失        | Log 未同步至遠端              | 檢查 log 設定或儲存權限                     |

---

## 💡 八、最佳實踐建議

✅ **建議：**

* 生產環境中使用多個 Worker 節點（Celery / K8s）。
* 調整 `worker_concurrency` 以符合硬體資源。
* 搭配集中式 log 儲存（如 S3, GCS, Elasticsearch）。
* 監控 Worker 心跳與任務成功率。

⚠️ **避免：**

* 所有任務都集中在同一台 Worker 上執行。
* 在 Worker 內部執行長時間阻塞的同步任務（應外部化）。
* 忽略 log rotation 或未設定 log retention。

---

## 🧭 九、總覽：Scheduler、Executor、Worker 關係

```
       +-----------------------------+
       |          Scheduler          |
       | 判斷任務應執行週期            |
       +-------------+---------------+
                     |
                     v
       +-----------------------------+
       |          Executor           |
       | 將任務分派至可用 Worker       |
       +-------------+---------------+
                     |
                     v
       +-----------------------------+
       |            Worker            |
       | 實際執行任務邏輯並回報結果     |
       +-----------------------------+
```

---

> ✅ **結論：** Worker 是 Airflow 任務執行的最終環節。不同 Executor 會影響 Worker 的部署與啟動方式。良好的 Worker 管理與監控，是確保整體 Airflow pipeline 穩定性的關鍵。
