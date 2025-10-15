"""
xcom_demo.py — Airflow SDK 範例：任務間資料交換（XCom）

功能概要：
- 示範如何透過 XCom 在任務之間傳遞資料。
- 使用 @task 定義兩個任務：producer() 與 consumer()。
- producer() 回傳字典，consumer() 接收並列印內容。

核心觀念：
1️⃣ Airflow 任務彼此獨立執行，無法直接傳遞 Python 變數。
2️⃣ 當任務有回傳值時，Airflow 會自動將結果序列化存入 XCom（Cross-Communication）。
3️⃣ 下游任務在以該輸出作為參數呼叫時，Airflow 於執行階段會自動還原並注入實際資料。

建議路徑：<your-project>/dags/xcom_demo.py
"""

# ---- 匯入 -----------------------------------------------------------------
from airflow.sdk import dag, task, Context
from typing import Dict, Any


# ---- 宣告 DAG -------------------------------------------------------------
@dag(
    description="Demonstrate XCom communication between tasks.",
    tags=["demo", "xcom"],
)
def xcom_demo():
    """DAG 主體：展示 XCom 自動傳遞任務結果的機制。"""

    # (1) 任務 producer ----------------------------------------------------
    @task
    def producer() -> Dict[str, Any]:
        """上游任務：建立字典資料並回傳。

        - 回傳值會自動存入 XCom（key='return_value'）。
        - 下游 consumer() 呼叫時會自動取出這份結果。
        """
        number = 42
        message = "Hello, Airflow!"
        print(f"[producer] Generated: number={number}, message='{message}'")
        return {"number": number, "message": message}

    # (2) 任務 consumer ----------------------------------------------------
    @task
    def consumer(payload: Dict[str, Any]):
        """下游任務：接收上游的回傳資料並輸出內容。"""
        print(f"[consumer] number = {payload['number']}")
        print(f"[consumer] message = {payload['message']}")

    # ---- 任務依賴設定 ----------------------------------------------------
    result = producer()   # 呼叫上游任務（回傳 XComArg 佔位符）
    consumer(result)      # 下游消費上游輸出 → 建立依賴鏈


# ---- 註冊 DAG -------------------------------------------------------------
xcom_demo()