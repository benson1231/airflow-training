"""
branching_demo.py — Airflow SDK 分支控制（Branching）範例

功能概要：
- 展示如何使用 @task.branch 依條件決定任務路徑。
- 根據上游任務 num_source() 的輸出，選擇執行 match_one() 或 not_one()。

DAG 結構：
┌────────────────┐
│  num_source()  │
└──────┬─────────┘
       │
       ▼
┌───────────────┐
│   selector()  │ ← 分支控制任務
└──────┬────────┘
       ├────────────▶ match_one()
       └────────────▶ not_one()

- 若 num_source() 回傳 1，執行 match_one()
- 若回傳其他值，執行 not_one()

建議路徑：<your-project>/dags/branching_demo.py
"""

# ---- 匯入 -----------------------------------------------------------------
from airflow.sdk import dag, task


# ---- 宣告 DAG -------------------------------------------------------------
@dag(
    description="Demonstration of conditional branching in Airflow SDK.",
    tags=["demo", "branching"],
)
def branching_demo():
    """DAG 主體：展示分支條件與任務選擇邏輯。"""

    # (1) 數值來源任務 ----------------------------------------------------
    @task
    def num_source() -> int:
        """產生整數作為分支依據。"""
        return 1

    # (2) 分支決策任務 ----------------------------------------------------
    @task.branch
    def selector(num: int) -> str:
        """根據傳入數值選擇後續要執行的任務。

        - 若 num == 1 → 執行 match_one
        - 否則 → 執行 not_one

        Airflow 根據回傳的 task_id 只會啟動對應任務，
        其他任務自動標記為 skipped。
        """
        if num == 1:
            return "match_one"
        return "not_one"

    # (3) 分支任務 1 ------------------------------------------------------
    @task
    def match_one(num: int):
        """當 num == 1 時執行的任務。"""
        print(f"Number equals {num}.")

    # (4) 分支任務 2 ------------------------------------------------------
    @task
    def not_one(num: int):
        """當 num != 1 時執行的任務。"""
        print(f"Number differs from one: {num}")

    # ---- 任務依賴設定 ----------------------------------------------------
    value = num_source()             # 呼叫 num_source()，回傳 XComArg（佔位符）
    selector(value) >> [match_one(value), not_one(value)]  # 建立分支依賴鏈


# ---- 註冊 DAG -------------------------------------------------------------
branching_demo()