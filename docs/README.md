# Airflow Documentation Index

詳見: [airflow官方文檔](https://airflow.apache.org/docs/apache-airflow/stable/index.html), [Astro CLI官方文檔](https://www.astronomer.io/docs/astro/cli/overview) 與 [astronomer-Learn Airflow 3文檔](https://www.astronomer.io/docs/learn)

以下為本專案 `docs/` 目錄中的文件索引。點擊檔名可直接開啟對應章節，右欄為簡短說明：

---

## 🧩 Authoring — DAG 撰寫與設計

| 連結                                                                     | 說明                                    |
| ---------------------------------------------------------------------- | ------------------------------------- |
| [authoring/assets.md](authoring/assets.md)                             | 使用 @asset 建立資料資產與血緣關係                 |
| [authoring/branching.md](authoring/branching.md)                       | 條件分支與任務決策邏輯 (BranchPythonOperator 等)  |
| [authoring/dags.md](authoring/dags.md)                                 | DAG 結構與定義方式概述                         |
| [authoring/datasets.md](authoring/datasets.md)                         | Dataset 與資料觸發機制介紹                     |
| [authoring/dependencies.md](authoring/dependencies.md)                 | 任務間依賴關係設定與可視化                         |
| [authoring/dynamic_dags.md](authoring/dynamic_dags.md)                 | 動態建立 DAG 的設計與實作方法                     |
| [authoring/dynamic_task_mapping.md](authoring/dynamic_task_mapping.md) | 動態任務映射與平行化應用                          |
| [authoring/hooks.md](authoring/hooks.md)                               | Hooks 連結外部系統的用途與自訂教學                  |
| [authoring/operator.md](authoring/operator.md)                         | Operators 的種類與自訂範例                    |
| [authoring/sensor.md](authoring/sensor.md)                             | Sensors 與等待條件的使用方式                    |
| [authoring/task_flow.md](authoring/task_flow.md)                       | TaskFlow API：以 @task 撰寫 Python 原生 DAG |
| [authoring/task_group.md](authoring/task_group.md)                     | 使用 TaskGroup 組織 DAG 結構                |
| [authoring/templating.md](authoring/templating.md)                     | Jinja2 模板與變數渲染應用                      |
| [authoring/variable.md](authoring/variable.md)                         | Airflow 變數管理與安全性注意事項                  |
| [authoring/xcom.md](authoring/xcom.md)                                 | XCom 任務間資料傳遞與實務示例                     |

---

## ⚙️ Concepts — 核心概念與運作原理

| 連結                                               | 說明                         |
| ------------------------------------------------ | -------------------------- |
| [concepts/connection.md](concepts/connection.md) | Airflow Connection 機制與後端設定 |
| [concepts/executor.md](concepts/executor.md)     | Executor 架構與任務執行原理         |
| [concepts/provider.md](concepts/provider.md)     | Provider 套件架構與外部擴充方式       |
| [concepts/scheduler.md](concepts/scheduler.md)   | Scheduler 排程器運作流程與任務分派     |
| [concepts/timezone.md](concepts/timezone.md)     | Airflow 時區設定與排程對應原理        |
| [concepts/trigger.md](concepts/trigger.md)       | Triggers 與非同步事件監控機制        |
| [concepts/worker.md](concepts/worker.md)         | Worker 節點角色與任務處理模式         |
| [concepts/README.md](concepts/README.md)         | 本章概述與核心架構導讀                |

---

## 🚀 Deployment — 部署與環境管理

| 連結                                                             | 說明                        |
| -------------------------------------------------------------- | ------------------------- |
| [deployment/astro-cli.md](deployment/astro-cli.md)             | 使用 Astronomer CLI 進行開發與部署 |
| [deployment/cron_expression.md](deployment/cron_expression.md) | Cron 語法與排程時間表設計           |
| [deployment/logging.md](deployment/logging.md)                 | 任務與系統日誌配置與監控              |
| [deployment/versioning.md](deployment/versioning.md)           | DAG 與環境版本控制策略             |

---

## 🔁 Workflow — 工作流與執行實務

| 連結                                                       | 說明              |
| -------------------------------------------------------- | --------------- |
| [workflow/best_practices.md](workflow/best_practices.md) | DAG 開發與維運最佳實踐建議 |
| [workflow/dag_run.md](workflow/dag_run.md)               | DAG 執行生命周期與重跑機制 |
| [workflow/scheduling.md](workflow/scheduling.md)         | 任務排程與時間間隔控制教學   |
| [workflow/testing.md](workflow/testing.md)               | DAG 測試與單元驗證方法   |

---

## 🖼️ Images — 示意圖與架構圖

| 連結           | 說明                       |
| ------------ | ------------------------ |
| [img/](img/) | 包含 Airflow 架構、DAG 與流程示意圖 |

---

> 📘 建議：依主題循序閱讀，或使用搜尋快速定位（如輸入 *scheduler*、*XCom*、*Astro CLI* 等關鍵字）。
