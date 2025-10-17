"""
group_taskgroup_demo.py — Airflow SDK 的任務群組（TaskGroup）範例

功能概要：
- 展示如何利用 @task_group 建立層級化任務結構。
- 範例中包含外層群組與內層巢狀群組。
- 使用 default_args 於群組層級設定預設的重試次數。

DAG 結構：
┌────────────┐     ┌────────────────────────┐
│  source()  │ →   │  outer_group(result)   │
└────────────┘     └────────────────────────┘
                    ├── transform()
                    └── nested_group()
                            └── finalize()

建議路徑：<your-project>/dags/group_taskgroup_demo.py
"""

# ---- 匯入 -----------------------------------------------------------------
from airflow.sdk import dag, task, task_group


# ---- 宣告 DAG -------------------------------------------------------------
@dag(
    description="Nested TaskGroup example with retry settings.",
    tags=["demo", "taskgroup"],
)
def group_taskgroup_demo():
    """DAG 主體：展示外層與巢狀 TaskGroup 的使用方式。"""

    # (1) 單一任務 source --------------------------------------------------
    @task
    def source() -> int:
        """上游任務：產生整數 42。

        - 輸出值會傳遞給外層群組 outer_group 作為輸入參數。
        - 任務輸出會自動透過 XCom 傳遞至下游。
        """
        return 42

    # (2) 外層任務群組 outer_group -----------------------------------------
    @task_group(default_args={"retries": 2})
    def outer_group(result: int):
        """外層 TaskGroup：接收上游 source() 的結果作為輸入。

        - 群組層級的 default_args（retries=2）會套用給群組內所有任務。
        - 包含 transform() 與內層 nested_group()。
        """

        # --- 子任務 transform --------------------------------------------
        @task
        def transform(value: int):
            """處理輸入數值並列印結果。"""
            print(f"Transformed value: {value + 42}")

        # --- 內層巢狀群組 nested_group ----------------------------------
        @task_group(default_args={"retries": 3})
        def nested_group():
            """巢狀 TaskGroup：具有自己重試設定（retries=3）。"""

            @task
            def finalize():
                """最終任務：列印完成訊息。"""
                print("Nested task complete.")

            # 執行群組內任務
            finalize()

        # 群組內依賴設定：transform → nested_group
        transform(result) >> nested_group()

    # ---- 主流程依賴設定 ---------------------------------------------------
    output = source()        # 呼叫 source() 並取得 XComArg 物件
    outer_group(output)      # 將結果傳遞至外層群組


# ---- 註冊 DAG -------------------------------------------------------------
group_taskgroup_demo()