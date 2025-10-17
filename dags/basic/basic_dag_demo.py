"""
basic_dag_demo.py — Airflow SDK（@dag / @task）最小可執行範例

功能概要：
- 展示 Airflow SDK decorator API 的基本結構與資料流。
- 範例由三個任務組成：step_a → step_b → step_c。
- 說明排程設定、XCom 傳遞與依賴關係定義。

DAG 流程：
┌───────────┐     ┌───────────┐     ┌────────────┐
│ step_a()  │ →   │ step_b()  │ →   │ step_c()   │
└───────────┘     └───────────┘     └────────────┘

建議路徑：<your-project>/dags/basic_dag_demo.py
"""

# ---- 匯入 -----------------------------------------------------------------
from airflow.sdk import dag, task  # Airflow SDK decorator 入口
from pendulum import datetime      # 處理時區與日期時間建議使用 pendulum


# ---- 宣告 DAG -------------------------------------------------------------
@dag(
    start_date=datetime(2025, 1, 1),   # DAG 起始邏輯日期
    schedule="@daily",                # 每天排程一次
    description="Minimal DAG demo with three sequential tasks.",
    tags=["basic"],
)
def basic_dag_demo():
    """DAG 主體：定義任務及其依賴關係。"""

    # (1) 任務 A ----------------------------------------------------------
    @task
    def step_a() -> int:
        """上游任務：回傳整數 1 作為下游輸入。"""
        # 若要測試錯誤與重試，可解除下列註解：
        # raise ValueError("Intentional error for retry demo")
        return 1

    # (2) 任務 B ----------------------------------------------------------
    @task
    def step_b(value: int) -> int:
        """中間任務：接收 step_a 的結果並加 1。"""
        return value + 1

    # (3) 任務 C ----------------------------------------------------------
    @task
    def step_c() -> None:
        """下游任務：執行最終動作（此例僅列印訊息）。"""
        print("Pipeline complete — Hello Airflow!")

    # ---- 任務依賴設定 ----------------------------------------------------
    a_out = step_a()           # 呼叫上游任務 → 回傳 XComArg（非實值）
    b_out = step_b(a_out)      # step_b 依賴 step_a 的結果
    b_out >> step_c()          # step_c 在 step_b 完成後執行


# ---- 註冊 DAG -------------------------------------------------------------
basic_dag_demo()