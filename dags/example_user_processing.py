"""
example_user_processing.py — Airflow SDK + SQL + Sensor 綜合範例，含詳細中文註解

說明：
此 DAG 示範了 Airflow 新版 SDK API 寫法，結合：
1) SQLExecuteQueryOperator 建立 Postgres 資料表
2) Sensor 任務（以 HTTP 請求偵測外部 API 是否可用）
3) @task 函式串接資料萃取、轉換與載入（ETL 概念）
4) PostgresHook.copy_expert 將結果 CSV 寫入資料庫

DAG 流程概念：
┌──────────────┐    ┌──────────────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐
│ create_table │ ─→ │   is_api_available   │ ─→ │ extract_user │ ─→ │ process_user │ ─→ │ store_user │
└──────────────┘    └──────────────────────┘    └──────────────┘    └──────────────┘    └────────────┘
"""

# ---- 匯入必要模組 ----------------------------------------------------------
from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook


# ---- 定義 DAG --------------------------------------------------------------
@dag
# decorator 沒有參數時，Airflow 仍會以預設 start_date、catchup=False 等屬性建立 DAG
# 你也可寫成：
# @dag(start_date=datetime(2025,1,1), schedule="@daily", catchup=False)
def user_processing():
    """DAG 主體：以 PostgreSQL + API 為例的簡易 ETL 流程"""

    # ----------------------------------------------------------------------
    # (1) 建立資料表
    # ----------------------------------------------------------------------
    create_table = SQLExecuteQueryOperator(
        task_id="create_table",       # 任務名稱
        conn_id="postgres",           # Airflow 連線 ID（在 UI 中設定 Connections）
        sql="""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ----------------------------------------------------------------------
    # (2) 感測任務：檢查 API 是否可用
    # ----------------------------------------------------------------------
    @task.sensor(poke_interval=30, timeout=300)
    def is_api_available() -> PokeReturnValue:
        """Sensor 任務：每隔 30 秒呼叫一次 API，直到成功或超時（5 分鐘）。"""
        import requests
        response = requests.get("https://raw.githubusercontent.com/marclamberti/datasets/refs/heads/main/fakeuser.json")
        print("API 回應狀態碼：", response.status_code)

        if response.status_code == 200:
            condition = True                    # 條件達成：API 可用
            fake_user = response.json()          # 將回傳內容（JSON）傳遞給下游
        else:
            condition = False
            fake_user = None

        # 回傳 PokeReturnValue 物件：
        # is_done=True 表示 sensor 可結束；xcom_value 會存入 XCom 給下游任務。
        return PokeReturnValue(is_done=condition, xcom_value=fake_user)

    # ----------------------------------------------------------------------
    # (3) 萃取任務：解析 fake_user JSON
    # ----------------------------------------------------------------------
    @task
    def extract_user(fake_user: dict) -> dict:
        """從 fake_user JSON 中抽出特定欄位。"""
        return {
            "id": fake_user["id"],
            "firstname": fake_user["personalInfo"]["firstName"],
            "lastname": fake_user["personalInfo"]["lastName"],
            "email": fake_user["personalInfo"]["email"],
        }

    # ----------------------------------------------------------------------
    # (4) 處理任務：新增時間戳記並輸出 CSV
    # ----------------------------------------------------------------------
    @task
    def process_user(user_info: dict) -> None:
        """將使用者資訊加上 created_at 欄位並存成 CSV。"""
        import csv
        from datetime import datetime

        # 加入時間戳記
        user_info["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 輸出到暫存檔案
        with open("/tmp/user_info.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=user_info.keys())
            writer.writeheader()
            writer.writerow(user_info)

        print("已輸出 /tmp/user_info.csv")

    # ----------------------------------------------------------------------
    # (5) 載入任務：將 CSV 寫入 Postgres
    # ----------------------------------------------------------------------
    @task
    def store_user() -> None:
        """將 CSV 檔內容以 COPY 命令匯入 Postgres users 資料表。"""
        hook = PostgresHook(postgres_conn_id="postgres")
        hook.copy_expert(
            sql="COPY users FROM STDIN WITH CSV HEADER",
            filename="/tmp/user_info.csv"
        )
        print("✅ 已將資料匯入 users 表。")

    # ----------------------------------------------------------------------
    # (6) 串接 DAG 任務依賴
    # ----------------------------------------------------------------------
    # create_table → is_api_available → extract_user → process_user → store_user

    process_user(
        extract_user(
            create_table >> is_api_available()  # create_table 執行完後才啟動 sensor
        )
    ) >> store_user()


# ---- 呼叫 DAG -------------------------------------------------------------
user_processing()