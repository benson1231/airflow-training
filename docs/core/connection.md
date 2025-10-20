# Airflow Connections

**2025.10.20**

本章介紹 Airflow 中的 **Connection（連線設定）** 概念、用途、管理方式與實作範例。Connections 是 Airflow 與外部系統（如資料庫、雲端服務、API、FTP 等）互動的基礎設定。

---

## 🧭 一、Connection 基本概念

在 Airflow 中，許多 Operators（如 `PostgresOperator`、`S3Hook`、`HttpSensor`）都需要連線至外部服務。為避免硬編碼憑證，Airflow 提供集中管理的 **Connections**。

**每個 Connection 包含以下基本欄位：**

| 欄位名稱      | 說明                                                |
| --------- | ------------------------------------------------- |
| Conn Id   | 連線識別名稱（在程式中引用）                                    |
| Conn Type | 連線類型，例如 `Postgres`, `MySQL`, `HTTP`, `AWS`, `GCP` |
| Host      | 伺服器或服務位址（hostname/IP）                             |
| Schema    | 資料庫名稱或連線架構（可選）                                    |
| Login     | 使用者名稱（如 DB 帳號）                                    |
| Password  | 密碼（Airflow 會加密儲存於 metadata DB）                    |
| Port      | 連接埠號（如 5432, 3306）                                |
| Extra     | JSON 格式的額外設定（如憑證路徑、region、API token 等）            |

> 📘 **備註**：Connections 儲存在 metadata database 的 `connection` table，並可透過 UI、CLI 或環境變數設定。

---

## ⚙️ 二、建立與管理 Connection

### 1️⃣ Airflow Web UI

![Airflow connection](../img/connection.png)

1. 進入 **Admin → Connections**。
2. 點擊 **+ Add a new record**。
3. 填寫必要欄位（Conn Id、Conn Type、Host、Login 等）。
4. 儲存後即可在 DAG 中以 `conn_id` 參照。

### 2️⃣ CLI 建立 Connection

```bash
airflow connections add my_postgres_conn \
    --conn-type postgres \
    --conn-host mydb.example.com \
    --conn-login airflow_user \
    --conn-password secret_pw \
    --conn-schema mydb \
    --conn-port 5432
```

刪除：

```bash
airflow connections delete my_postgres_conn
```

列出：

```bash
airflow connections list
```

查看詳細資訊：

```bash
airflow connections get my_postgres_conn
```

### 3️⃣ 以環境變數建立

在環境中設定：

```bash
export AIRFLOW_CONN_MY_POSTGRES_CONN='postgresql://airflow_user:secret_pw@mydb.example.com:5432/mydb'
```

> 🔑 命名規則：`AIRFLOW_CONN_<CONN_ID>`（轉為大寫並以底線代替 dash）。

此方式特別適合容器化（如 Docker）部署環境，能透過 `.env` 或 Secrets 管理憑證。

---

## 🧩 三、在 DAG 中使用 Connection

範例：以 `PostgresHook` 從 Connection 取得資料。

```python
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import dag, task

@dag(schedule=None, start_date=datetime(2025,1,1))
def connection_demo():

    @task
    def fetch_data():
        hook = PostgresHook(postgres_conn_id='my_postgres_conn')
        records = hook.get_records('SELECT COUNT(*) FROM users;')
        print(f"User count: {records[0][0]}")

    fetch_data()

connection_demo()
```

Airflow 將自動讀取 `my_postgres_conn` 的設定內容，建立連線物件並執行查詢。

---

## 🧰 四、常見 Connection 類型

| Conn Type               | 說明                   | Provider Package                     |
| ----------------------- | -------------------- | ------------------------------------ |
| `postgres`              | PostgreSQL 資料庫       | `apache-airflow-providers-postgres`  |
| `mysql`                 | MySQL / MariaDB      | `apache-airflow-providers-mysql`     |
| `http`                  | 一般 API 呼叫            | `apache-airflow-providers-http`      |
| `aws`                   | AWS S3、Lambda、Glue 等 | `apache-airflow-providers-amazon`    |
| `google_cloud_platform` | GCP BigQuery、Storage | `apache-airflow-providers-google`    |
| `slack`                 | Slack 通知             | `apache-airflow-providers-slack`     |
| `snowflake`             | Snowflake 資料倉儲       | `apache-airflow-providers-snowflake` |
| `mongo`                 | MongoDB              | `apache-airflow-providers-mongo`     |

> 💡 若 Operator 無法找到對應 Provider，需先安裝相應套件（例如：`pip install apache-airflow-providers-postgres`）。

---

## 🧠 五、安全與最佳實踐

* **❌ 不建議** 在 DAG code 中硬編碼密碼或 Token。
* ✅ 使用 **Connection + Secret Backend（如 AWS Secret Manager 或 HashiCorp Vault）**。
* ✅ 對生產環境的敏感憑證設定，使用環境變數或加密後的 metadata DB。
* ✅ 建議以組織規模統一命名，例如：`aws_s3_prod`、`postgres_staging_userdb`。

---

## 🔍 六、除錯與驗證

若任務報錯顯示無法取得連線：

1. 確認 Connection 名稱拼寫與 `conn_id` 一致。
2. 檢查 Airflow Web UI → Admin → Connections 是否存在。
3. 確認 Provider 已安裝並支援該連線類型。
4. 可使用 CLI 測試連線：

   ```bash
   airflow connections get my_postgres_conn
   ```

---

> ✅ **總結**：Connection 是 Airflow 與外部資源溝通的橋樑。妥善設定與命名能提高 DAG 可重用性與安全性，是建構可維護資料管線的重要一環。
