# Airflow Logging（日誌系統）

**2025.10.22**

## 🧩 概念簡介
Airflow 的 **Logging 機制** 用於追蹤 DAG、任務（Task）與系統元件（Scheduler、Executor、Worker）的執行情況。所有 log 皆可集中管理、搜尋與分析，協助除錯與稽核。

Airflow 的日誌分為三層：
1. **Scheduler logs**：DAG 排程與觸發紀錄。
2. **Task logs**：每個任務執行的輸出、錯誤、重試紀錄。
3. **Webserver logs**：Web UI 行為、API 請求與存取記錄。

---

## ⚙️ 本地與遠端記錄設定
### 本地端（Local logging）
預設情況下，Airflow 將日誌儲存在：
```bash
$AIRFLOW_HOME/logs/
```
每個 DAGRun 與 TaskInstance 皆會建立獨立資料夾：
```
logs/<dag_id>/<task_id>/<execution_date>/1.log
```

### 遠端儲存（Remote logging）
若需在多節點環境（如 CeleryExecutor）集中管理 log，可啟用遠端紀錄：
```ini
[logging]
remote_logging = True
remote_log_conn_id = my_s3_conn
remote_base_log_folder = s3://airflow-logs
logging_level = INFO
```
支援的後端包括：
- Amazon S3 (`s3://`)
- Google Cloud Storage (`gs://`)
- Azure Blob Storage (`wasb://`)
- Elasticsearch（透過 ElasticSearchTaskHandler）

---

## 🧱 Log Handler 類型
Airflow 使用 Python 的 `logging` 模組，可在 `airflow.cfg` 或自訂模組中指定 Handler：

| Handler 類型 | 功能 |
|---------------|------|
| `file.task` | 預設任務輸出至本地檔案 |
| `stream` | 將輸出顯示於 console（如 `docker logs`） |
| `elasticsearch` | 將任務 log 傳送至 Elasticsearch cluster |
| `gcs`、`s3`、`wasb` | 將 log 上傳雲端儲存 |

---

## 🧩 自訂 Logging Config
可建立自訂 logging 設定檔 `custom_logging_config.py`，並在 `airflow.cfg` 中引用：
```ini
[logging]
logging_config_class = custom_logging_config.LOGGING_CONFIG
```

範例：
```python
import logging
from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG

LOGGING_CONFIG = DEFAULT_LOGGING_CONFIG.copy()
LOGGING_CONFIG['handlers']['console']['formatter'] = 'airflow'
LOGGING_CONFIG['handlers']['console']['class'] = 'logging.StreamHandler'
LOGGING_CONFIG['loggers']['airflow.task'] = {
    'handlers': ['console'],
    'level': 'INFO',
}
```

---

## 🔁 Log Rotation 與保留策略
長期運行的 DAG 容易累積大量日誌，建議定期清理：

### 方法一：設定 rotation
可在系統層（logrotate）或 Docker volume 中設定自動清理，例如：
```bash
/usr/local/airflow/logs/*.log {
    daily
    rotate 14
    compress
    missingok
}
```

### 方法二：Airflow CLI 清理
```bash
airflow tasks clear my_dag --start-date 2025-01-01 --end-date 2025-01-31 --only-logs
```
或：
```bash
airflow dags delete my_dag --yes --keep-logs False
```

---

## 🧰 實務技巧與建議
1. **開啟 remote_logging**：在分散式執行環境（Celery、Kubernetes）中集中 log。
2. **保留錯誤堆疊（traceback）**：方便除錯任務失敗原因。
3. **善用 UI filter**：可直接從 Web UI 檢視特定 task log。
4. **統一格式**：透過 `log_format` 與 `hostname_callable`，記錄 hostname、execution_date、run_id。
5. **重要 log 上傳至外部觀測平台**：如 CloudWatch、Grafana Loki 或 Elastic Stack。

---

## 🧭 CLI 指令快速查閱
| 指令 | 說明 |
|-------|------|
| `airflow tasks logs <dag_id> <task_id> <execution_date>` | 查看任務 log |
| `airflow tasks clear <dag_id> --only-logs` | 清除 log |
| `airflow info` | 顯示當前 logging 設定 |
| `docker logs airflow-worker` | 查看容器 log |

---

## 🧩 小結
Airflow Logging 不僅是除錯工具，更是 pipeline 健康監控的重要基礎。透過合理的 log handler、集中式儲存與定期 rotation，可確保系統穩定、安全且易於追蹤。