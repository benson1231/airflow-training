# Airflow 架構概觀（Architecture Overview）

![Airflow Architecture Diagram](../img/arch-diag-basic.png)

此圖來自 Airflow 官網，展示了 **Apache Airflow** 的基本架構與各組件間的互動流程。Airflow 採用模組化設計，透過 Web 伺服器、排程器、執行器與工作節點協同運作，以完成任務的排程與執行。

---

## 一、主要組件與用途

| 組件名稱                                    | 功能說明                                                            | 主要互動對象                               |
| --------------------------------------- | --------------------------------------------------------------- | ------------------------------------ |
| **Data Engineer**                       | 工作流程的作者，撰寫 DAG（Python 形式）並上傳至 Airflow。                          | DAGs、Web Server                      |
| **DAGs (Directed Acyclic Graphs)**      | 定義任務與依賴關係的流程圖。每個 DAG 代表一個 Pipeline。                             | Scheduler、Web Server                 |
| **Web Server**                          | 提供 Airflow UI，讓使用者可視化 DAG 狀態、執行任務、檢視日誌。                         | User Interface、Scheduler、Metadata DB |
| **User Interface (UI)**                 | 使用者操作入口，提供 DAG 執行監控、Trigger、Logs 查閱等功能。                         | Web Server、Data Engineer             |
| **Scheduler**                           | 負責根據 DAG 排程邏輯觸發任務，並將可執行的任務交給 Executor。                          | Metadata DB、Executor、Web Server      |
| **Executor**                            | 任務分配器，負責將任務送交 Worker 執行。不同執行模式（Local、Celery、Kubernetes）會影響執行方式。 | Scheduler、Workers                    |
| **Worker(s)**                           | 真正執行任務的節點（可為容器、VM 或 Pod），執行完成後回報狀態與結果。                          | Executor、Metadata DB                 |
| **Metadata Database (Postgres, MySQL)** | 儲存 Airflow 的所有執行紀錄、任務狀態、連線設定與變數。                                | Scheduler、Web Server、Executor        |
| **Airflow.cfg**                         | Airflow 的全域設定檔，控制環境參數（如 Executor 類型、資料庫連線、Web 服務設定）。            | 所有核心模組                               |

---

## 二、執行流程摘要

1. **Data Engineer 撰寫 DAG** → 儲存在 `dags/` 目錄。
2. **Scheduler 掃描 DAG** → 根據設定決定何時觸發任務。
3. **Scheduler 將任務交給 Executor** → 負責分派至適當的 Worker。
4. **Worker 執行任務** → 執行結果與日誌回傳至 Metadata DB。
5. **Web Server/UI 顯示任務狀態** → 提供圖形化介面供使用者監控。

---

## 三、常見 Executor 類型

| Executor 類型            | 特點                                                | 適用情境         |
| ---------------------- | ------------------------------------------------- | ------------ |
| **SequentialExecutor** | 單執行緒，任務依序執行（預設模式）                                 | 測試環境、開發階段    |
| **LocalExecutor**      | 多執行緒本機平行執行                                        | 單機多任務開發      |
| **CeleryExecutor**     | 任務分散至多台 Worker，使用 Celery Broker（如 Redis、RabbitMQ） | 分散式生產環境      |
| **KubernetesExecutor** | 每個任務以 Pod 型式執行，支援自動伸縮                             | 雲端部署或容器化生產環境 |

---

## 四、Airflow 元件協作摘要

| 流程階段   | 關鍵互動                        | 結果            |
| ------ | --------------------------- | ------------- |
| DAG 掃描 | Scheduler → DAGs            | 載入所有已定義的工作流程  |
| 任務觸發   | Scheduler → Executor        | 任務進入執行佇列      |
| 任務執行   | Executor → Worker(s)        | 實際執行任務邏輯      |
| 狀態回報   | Worker(s) → Metadata DB     | 儲存任務完成或失敗紀錄   |
| 狀態顯示   | Metadata DB → Web Server/UI | 使用者可即時監控與重試任務 |

---

## 五、補充：Airflow.cfg 常見設定項目

| 參數名稱               | 用途                  | 範例                                                       |
| ------------------ | ------------------- | -------------------------------------------------------- |
| `executor`         | 指定使用的執行器類型          | `LocalExecutor`、`CeleryExecutor`                         |
| `sql_alchemy_conn` | 指定 Metadata DB 連線字串 | `postgresql+psycopg2://airflow:airflow@postgres/airflow` |
| `dags_folder`      | DAG 檔案所在路徑          | `/usr/local/airflow/dags`                                |
| `base_url`         | Airflow Web UI 位置   | `http://localhost:8080`                                  |
| `load_examples`    | 是否載入預設範例 DAG        | `False`                                                  |

---

### ✅ 總結

Airflow 的核心是由 **Scheduler、Executor、Worker、Web Server、Metadata Database** 組成的分層架構：

* Scheduler 負責任務排程。
* Executor 與 Worker 負責執行。
* Metadata DB 紀錄狀態。
* Web Server 與 UI 提供監控入口。

這樣的設計讓 Airflow 具備可擴充性與彈性，能夠支援從單機測試到分散式雲端部署的多種場景。
