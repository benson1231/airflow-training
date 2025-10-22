# Airflow Hooks

**2025.10.22**

## 🧭 一、Hooks 是什麼？

[Hook](https://www.astronomer.io/docs/learn/what-is-a-hook#hook-basics) 是 Airflow 與外部系統（如資料庫、API、儲存服務）之間的**介面層（interface layer）**。
它負責處理連線、認證與資料交換，提供一組統一的 Python API，讓 Operator 可以透過同一套邏輯讀寫不同來源。

📘 **簡單理解：**

> Hook = 抽象化的連線物件，用來封裝「如何連到外部服務」的細節。

---

## ⚙️ 二、核心功能

| 功能          | 說明                                                    |
| ----------- | ----------------------------------------------------- |
| 連線管理        | 透過 Airflow Connection (UI/CLI) 儲存登入資訊、憑證、端點等。         |
| 驗證與重試       | Hook 通常內建驗證、重試與 session 管理邏輯（例如 HTTP retries）。        |
| 資料抽象        | 將外部操作封裝成 Python 方法（例如 `get_records()`、`run_query()`）。 |
| Operator 整合 | 幾乎所有 Operator 都是透過 Hook 實際執行底層任務。                     |

---

## 🧩 三、常見 Hook 類別

| Hook 名稱                  | 說明                                 |
| ------------------------ | ---------------------------------- |
| `PostgresHook`           | 連接 PostgreSQL，提供查詢與批次執行功能。         |
| `MySqlHook`              | 操作 MySQL 資料庫。                      |
| `HttpHook`               | 向 REST API 發送 HTTP 請求（GET、POST 等）。 |
| `S3Hook`                 | 與 AWS S3 互動（上傳、下載、列出檔案）。           |
| `GoogleCloudStorageHook` | 存取 GCS（Google Cloud Storage）。      |
| `SlackHook`              | 發送訊息至 Slack。                       |
| `BaseHook`               | 所有 Hook 的基底類別，負責取得連線資訊。            |

---

## 🧪 四、程式範例：自訂 Hook 與使用方式

```python
from airflow.hooks.base import BaseHook
import requests

class MyApiHook(BaseHook):
    """範例：自訂 Hook 以連線至外部 API。"""

    def __init__(self, conn_id: str):
        super().__init__()
        self.conn_id = conn_id
        self.base_url = self.get_connection(conn_id).host

    def get_data(self, endpoint: str):
        """發送 GET 請求並回傳 JSON 結果。"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

# --- 在 DAG 中使用 ---

from airflow.decorators import dag, task
from pendulum import datetime

@dag(start_date=datetime(2025, 1, 1), schedule=None, catchup=False)
def hook_demo():

    @task
    def fetch_data():
        hook = MyApiHook(conn_id="my_api_conn")
        data = hook.get_data("status")
        print(data)

    fetch_data()

hook_demo()
```

📍在 Airflow UI → **Admin → Connections** 中建立連線：

```
Conn Id: my_api_conn
Conn Type: HTTP
Host: https://api.example.com
```

---

## 🧠 五、Hook vs Operator

| 類別           | 角色                 | 範例                                            |
| ------------ | ------------------ | --------------------------------------------- |
| **Hook**     | 負責連線與操作外部資源        | `PostgresHook().get_records()`                |
| **Operator** | 控制工作邏輯（task layer） | `PostgresOperator(sql="SELECT * FROM table")` |

📘 Operator 幾乎都是「包裝」 Hook 來執行，
例如：`S3ToRedshiftOperator` → 同時使用 `S3Hook` + `PostgresHook`。

---

## 🧱 六、Hook 的延伸與整合

* 🔒 **安全性整合**：支援連接 Airflow Secret Backend（AWS Secrets Manager、HashiCorp Vault）。
* 🔁 **重試與 session 管理**：多數 Hook 內建自動重試與連線回收機制。
* 🌩️ **外部憑證共用**：支援使用 connection extra fields（如 token、region、profile）。

---

## 💡 七、實務建議

1. **統一管理憑證**：所有密碼、API Key 應儲存在 Connection 或 Secret Backend。
2. **模組化設計**：將常用 Hook 封裝成自訂模組供團隊共用。
3. **避免在 DAG 中硬編密碼**：改用 `get_connection()` 動態讀取。
4. **測試時使用 Mock Hook**：可模擬外部連線回應避免實際呼叫 API。

---

✅ **總結**：Hook 是 Airflow 與外部世界的橋樑，提供標準化的連線與操作介面，確保 DAG 任務能在多樣環境中一致執行。
