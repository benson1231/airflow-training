"""
user_pipeline.py — Airflow SDK ETL 範例（完整中文註解版）

目的：
- 展示以 Airflow 新版 SDK（@dag / @task / sensor）撰寫一條簡潔的 ETL 流程。
- 包含：資料表初始化 → 等待外部 API 可用 → 解析欄位 → 寫成 CSV → 載入 Postgres。
- 著重在每個步驟的「用途、時機、上下文（XCom）、常見錯誤排查」。

工作流拓撲（由左至右）：
 ┌───────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────┐   ┌────────────┐
 │ initialize_db │ → │ wait_for_api │ → │  parse_user  │ → │ save_to_csv │ → │ load_to_db │
 └───────────────┘   └──────────────┘   └──────────────┘   └─────────────┘   └────────────┘

放置路徑建議：<your-project>/dags/user_pipeline.py
注意：DAG 檔名、dag_id 不必相同，但一致性便於維護。
"""

# ---- 匯入核心元件 ---------------------------------------------------------
from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook


# ---- 宣告 DAG -------------------------------------------------------------
@dag(
    # 可依需求新增：start_date、schedule、catchup 等參數
    # 例如：start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False
)
def user_pipeline():
    """以使用者資料為題材的 ETL 工作流。

    說明：
    - 在 DAG 解析階段（scheduler / webserver 載入 .py 時）僅會建立任務與依賴關係，
      任務函式本體只會在實際執行時由 worker 呼叫。
    - 以 decorator 方式宣告任務，能直接在 Python 中表達資料流與依賴（可讀性佳）。
    """

    # ------------------------------------------------------------------
    # 1) 初始化資料庫結構（若不存在則建立）
    # ------------------------------------------------------------------
    initialize_db = SQLExecuteQueryOperator(
        task_id="initialize_db",      # UI 中的任務名稱
        conn_id="postgres",           # 在 Airflow Connections 設定的連線 ID（Postgres）
        sql="""
        CREATE TABLE IF NOT EXISTS user_info (
            user_id INT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # 備註：
        # - 若要在多 schema 環境下控制 search_path，可改用 hook 或在 sql 中顯示指定。
        # - 欄位型別可依資料來源調整，這裡以 TEXT 為簡化示範。
    )

    # ------------------------------------------------------------------
    # 2) 感測外部 API 是否可用（輪詢直到成功或超時）
    # ------------------------------------------------------------------
    @task.sensor(poke_interval=20, timeout=240)
    def wait_for_api() -> PokeReturnValue:
        """以 HTTP GET 測試 API。

        參數：
        - poke_interval：每次輪詢間隔秒數。
        - timeout：總等待時間上限（秒）。超過即標記為失敗（可觸發重試）。

        回傳：
        - PokeReturnValue：is_done=True 代表條件達成，sensor 結束；
          xcom_value 會被寫入 XCom，供下游任務取用。
        """
        import requests

        url = "https://raw.githubusercontent.com/marclamberti/datasets/refs/heads/main/fakeuser.json"
        resp = requests.get(url, timeout=10)
        print(f"[wait_for_api] status={resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()  # 此 JSON 將透過 XCom 傳給 parse_user
            return PokeReturnValue(is_done=True, xcom_value=data)
        else:
            # 回傳 is_done=False → scheduler 會於下個 poke_interval 再次呼叫本任務
            return PokeReturnValue(is_done=False, xcom_value=None)

    # ------------------------------------------------------------------
    # 3) 解析 JSON，僅取關鍵欄位（轉換步驟）
    # ------------------------------------------------------------------
    @task
    def parse_user(raw: dict) -> dict:
        """從 API 回傳的 JSON 取出核心欄位，回傳字典以供後續使用。

        注意：
        - 這裡假設 JSON 結構固定，實務上應加入結構驗證與缺值處理。
        - 任務回傳值會自動經由 XCom 傳遞（key=return_value）。
        """
        info = raw.get("personalInfo", {})
        record = {
            "user_id": raw.get("id"),
            "first_name": info.get("firstName"),
            "last_name": info.get("lastName"),
            "email": info.get("email"),
        }
        print(f"[parse_user] parsed keys={list(record.keys())}")
        return record

    # ------------------------------------------------------------------
    # 4) 寫入 CSV（載入前的暫存檔）
    # ------------------------------------------------------------------
    @task
    def save_to_csv(user_record: dict) -> str:
        """將單筆資料加上 created_at 並輸出為 CSV 檔。

        回傳：
        - 產生的 CSV 路徑字串，作為下游 load_to_db 的輸入。

        注意事項：
        - Airflow 容器中常見的可寫路徑為 /tmp；若要跨任務共用檔案，請確保執行環境共用該路徑
          （例如同一容器、或將路徑掛載為 volume）。
        - 在 KubernetesExecutor / CeleryExecutor 下，建議改為上傳到物件儲存（S3/GCS）或資料庫。
        """
        import csv
        from datetime import datetime
        import os

        output_path = "/tmp/ml_user.csv"
        user_record = dict(user_record)  # 避免就地修改上游物件
        user_record["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=user_record.keys())
            writer.writeheader()
            writer.writerow(user_record)

        print(f"[save_to_csv] exported → {output_path}")
        return output_path

    # ------------------------------------------------------------------
    # 5) 將 CSV 匯入 Postgres（載入步驟）
    # ------------------------------------------------------------------
    @task
    def load_to_db(csv_path: str) -> None:
        """以 COPY 將 CSV 匯入 user_info 資料表。

        需求：
        - 在 Airflow Connections 頁面建立 ID 為 `postgres` 的連線（主機、帳密、資料庫名）。
        - Airflow 執行環境能存取 `csv_path`（檔案必須存在於相同節點/容器或共享卷）。

        常見錯誤：
        - "could not open file"：多半是路徑在不同容器節點，或權限不足。
        - schema 問題：可在 SQL 中改為 `COPY schema.table ...`。
        """
        hook = PostgresHook(postgres_conn_id="postgres")
        hook.copy_expert(
            sql="COPY user_info FROM STDIN WITH CSV HEADER",
            filename=csv_path,
        )
        print("[load_to_db] rows appended to user_info")

    # ------------------------------------------------------------------
    # 6) 宣告依賴關係（由左至右串接）
    # ------------------------------------------------------------------
    load_to_db(
        save_to_csv(
            parse_user(
                initialize_db >> wait_for_api()  # 先建表，再等 API 可用
            )
        )
    )


# ---- 讓 Airflow 註冊這個 DAG --------------------------------------------
user_pipeline()