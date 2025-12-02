# Airflow Executor 運作原理與種類總覽

**2025.10.22**

[Executor（執行器）](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/index.html)是 Airflow 的核心元件之一，負責決定「任務（Task）」實際如何被執行與分配在哪裡執行。換句話說，Scheduler 負責**排程任務**，而 Executor 負責**執行任務**。

---

## 🧩 一、Executor 的角色

整體架構可簡化為：

```
DAG 定義 → Scheduler 決定任務 → Executor 分配任務 → Worker 執行任務
```

* **Scheduler**：根據 DAG 規則判斷哪些任務應該執行。
* **Executor**：接收 Scheduler 發出的執行指令，並分派任務給本地或遠端 worker。
* **Worker**：實際運行任務邏輯（例如 Python、Bash、SQL）。

---

## ⚙️ 二、Executor 的種類

Airflow 支援多種 Executor，取決於部署規模與資源架構。

### 1️⃣ SequentialExecutor（預設、單執行緒，已不推薦）

| 特性   | 說明             |
| ---- | -------------- |
| 類型   | 單執行緒、本地執行      |
| 優點   | 簡單、無需額外設定      |
| 缺點   | 一次只能跑一個任務，效能最低 |
| 適用情境 | 測試環境、開發初期      |

設定範例：

```ini
[core]
executor = SequentialExecutor
```

---

### 2️⃣ LocalExecutor（多執行緒本地執行）

| 特性   | 說明               |
| ---- | ---------------- |
| 類型   | 多進程並行、本機運行       |
| 優點   | 支援並行任務，適合單機多核系統  |
| 缺點   | 不支援分散式架構（僅限單台主機） |
| 適用情境 | 小型生產或本地實驗環境      |

設定範例：

```ini
[core]
executor = LocalExecutor
```

---

### 3️⃣ CeleryExecutor（分散式、多 Worker）

| 特性   | 說明                                    |
| ---- | ------------------------------------- |
| 類型   | 分散式（Celery + Message Queue）           |
| 優點   | 可擴充、跨多節點並行執行任務                        |
| 缺點   | 需設定 Celery + Broker（Redis 或 RabbitMQ） |
| 適用情境 | 中大型部署、團隊協作環境                          |

架構示意：

```
Scheduler → Celery Broker (Redis/RabbitMQ) → Celery Workers → 任務執行
```

設定範例：

```ini
[core]
executor = CeleryExecutor

[celery]
broker_url = redis://redis:6379/0
result_backend = db+postgresql://airflow:airflow@postgres/airflow
worker_concurrency = 8
```

---

### 4️⃣ KubernetesExecutor（雲原生分散式）

| 特性   | 說明                     |
| ---- | ---------------------- |
| 類型   | 雲原生，每個任務在獨立 Pod 中執行    |
| 優點   | 高度擴充、資源隔離良好、支援自動伸縮     |
| 缺點   | 需具備 Kubernetes 環境與權限設定 |
| 適用情境 | 雲端部署、大規模動態資源需求         |

設定範例：

```ini
[core]
executor = KubernetesExecutor
```

可搭配 Helm chart 自動管理 Worker Pods：

```bash
helm install airflow apache-airflow/airflow \
  --set executor=KubernetesExecutor \
  --set airflow.image.tag=3.0.0
```

---

### 5️⃣ CeleryKubernetesExecutor（混合模式）

| 特性   | 說明                              |
| ---- | ------------------------------- |
| 類型   | 混合執行（Celery + Kubernetes）       |
| 優點   | 靈活選擇任務執行模式，兼顧穩定與擴展性             |
| 缺點   | 架構複雜，需同時管理 Broker 與 K8s Cluster |
| 適用情境 | 企業級 Airflow 雲端混合架構              |

設定範例：

```ini
[core]
executor = CeleryKubernetesExecutor
```

---

## 🧠 三、不同 Executor 的比較

| Executor 類型              | 並行能力      | 分散式 | 複雜度   | 適用環境       |
| ------------------------ | --------- | --- | ----- | ---------- |
| SequentialExecutor       | ❌ 單任務     | ❌   | ⭐     | 本地測試、學習    |
| LocalExecutor            | ✅ 多任務（本機） | ❌   | ⭐⭐    | 單機實驗、小型專案  |
| CeleryExecutor           | ✅ 多任務（分散） | ✅   | ⭐⭐⭐   | 中大型環境、多人協作 |
| KubernetesExecutor       | ✅ Pod 隔離  | ✅   | ⭐⭐⭐⭐  | 雲原生部署、大型組織 |
| CeleryKubernetesExecutor | ✅ 雙模式     | ✅   | ⭐⭐⭐⭐⭐ | 混合雲、高彈性架構  |

---

## 🔧 四、Executor 與 Scheduler、Worker 的關係

```
+-------------------+
|       DAGs        |
+---------+---------+
          |
          v
+-------------------+
|     Scheduler      |  ← 決定何時執行哪個任務
+---------+---------+
          |
          v
+-------------------+
|     Executor       |  ← 分派任務到 worker 或 Pod
+---------+---------+
          |
          v
+-------------------+
|      Worker(s)     |  ← 實際執行任務邏輯
+-------------------+
```

---

## 💡 五、實務選擇建議

| 環境          | 推薦 Executor              | 理由          |
| ----------- | ------------------------ | ----------- |
| 開發 / 測試     | SequentialExecutor       | 簡單、無外部依賴    |
| 單機多核        | LocalExecutor            | 支援並行、部署簡單   |
| 內部伺服器叢集     | CeleryExecutor           | 可分散多節點，效能穩定 |
| 雲端 / K8s 平台 | KubernetesExecutor       | 高度彈性、支援自動伸縮 |
| 混合雲企業環境     | CeleryKubernetesExecutor | 混合控制最佳彈性    |

---

## 🧭 六、檢查目前執行模式

可透過 CLI 或 UI 檢查當前使用的 Executor：

```bash
airflow config get-value core executor
```

或在 Web UI → **Admin → Configurations** 檢視 `core.executor` 設定。

---

> ✅ **總結：**
>
> * Executor 負責任務的實際執行方式，是 Airflow 架構的關鍵組件。
> * 不同 Executor 對應不同規模與基礎設施。
> * 選擇 Executor 時應考慮 **部署環境、資源彈性、維運複雜度**。
