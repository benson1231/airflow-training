"""
user_processing_demo.py — Airflow SDK + SQL + Sensor + PostgresHook 範例

功能概述：
- 先用 SQL operator 建立 PostgreSQL 資料表（users）。
- 使用 sensor 輪詢外部 API 是否可用，成功後將 JSON 存入 XCom。
- 將 JSON 解析（extract）、格式化並輸出成 CSV（process），最後以 COPY 匯入 Postgres（store）。

DAG 流程：
create_table → check_api_ready → parse_user → format_csv → import_user

建議路徑：<your-project>/dags/user_processing_demo.py
"""

# ---- 匯入 -----------------------------------------------------------------
from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook


# ---- 宣告 DAG -------------------------------------------------------------
@dag(
    description="ETL pipeline example using Airflow SDK, PostgreSQL, and HTTP sensor.",
    tags=["demo", "postgres", "sensor"],
)
def user_processing_demo():
    """DAG 主體：以 PostgreSQL 與外部 API 為例，展示 ETL 工作流程。"""

    # (1) 建表任務 ---------------------------------------------------------
    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id="postgres",
        sql="""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    )

    # (2) 感測任務 ---------------------------------------------------------
    @task.sensor(poke_interval=30, timeout=300)
    def check_api_ready() -> PokeReturnValue:
        """每 30 秒測試一次外部 API，最多等待 5 分鐘。"""
        import requests

        url = "https://raw.githubusercontent.com/marclamberti/datasets/refs/heads/main/fakeuser.json"
        response = requests.get(url, timeout=10)
        print(f"[check_api_ready] status: {response.status_code}")

        if response.status_code == 200:
            return PokeReturnValue(is_done=True, xcom_value=response.json())
        return PokeReturnValue(is_done=False, xcom_value=None)

    # (3) 萃取任務 ---------------------------------------------------------
    @task
    def parse_user(raw_user: dict) -> dict:
        """解析 JSON 結構並取出目標欄位。"""
        return {
            "id": raw_user["id"],
            "firstname": raw_user["personalInfo"]["firstName"],
            "lastname": raw_user["personalInfo"]["lastName"],
            "email": raw_user["personalInfo"]["email"],
        }

    # (4) 格式化任務 -------------------------------------------------------
    @task
    def format_csv(user_data: dict) -> None:
        """將解析後的資料加上時間戳並寫入 CSV。"""
        import csv
        from datetime import datetime

        user_data = dict(user_data)
        user_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        path = "/tmp/user_info.csv"
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=user_data.keys())
            writer.writeheader()
            writer.writerow(user_data)

        print(f"[format_csv] CSV saved at {path}")

    # (5) 匯入任務 ---------------------------------------------------------
    @task
    def import_user() -> None:
        """以 COPY 將 /tmp/user_info.csv 匯入 PostgreSQL。"""
        hook = PostgresHook(postgres_conn_id="postgres")
        hook.copy_expert(
            sql="COPY users FROM STDIN WITH CSV HEADER",
            filename="/tmp/user_info.csv",
        )
        print("[import_user] Data imported into users table.")

    # (6) 任務依賴設定 ----------------------------------------------------
    # create_table → check_api_ready → parse_user → format_csv → import_user
    format_csv(
        parse_user(
            create_table >> check_api_ready()
        )
    ) >> import_user()


# ---- 註冊 DAG -------------------------------------------------------------
user_processing_demo()