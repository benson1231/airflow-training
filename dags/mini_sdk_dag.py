"""
mini_sdk_dag.py — 使用 Airflow SDK 撰寫的極簡 DAG（含完整中文註解）

目的：
- 以最小可行的結構展示 @dag / @task 的用法與依賴串接。
- 重新命名、重新敘述與調整說明，避免與既有教材雷同。

重點：
1) 以 decorator 宣告 DAG 與任務，提升可讀性。
2) 利用 XCom（隱式）傳遞上游回傳值給下游。
3) schedule 與 start_date 決定排程點的生成。

建議放置：<your-project>/dags/mini_sdk_dag.py
"""

# ---- 匯入必要模組 ---------------------------------------------------------
from airflow.sdk import dag, task  # 新版 SDK 的 decorator 入口
from pendulum import datetime       # 建議用 pendulum 處理時區與日期


# ---- 宣告 DAG -------------------------------------------------------------
@dag(
    # 這裡指定第一個排程點的起始時間（不是立即執行）。
    # scheduler 會根據 start_date 與 schedule 計算出每次的 logical run。
    start_date=datetime(2025, 1, 1),

    # 使用預設的每日排程。也可改為 cron（例如 "0 2 * * *"）。
    schedule="@daily",

    # 可依需要加入：catchup=False、default_args、tags 等參數。
)
def mini_pipeline():
    """最小化示例：三個任務依序執行，展示資料在任務間的傳遞方式。

    在 DAG 解析階段：
    - Airflow 只會建立任務定義與依賴（並不執行任務本體）。
    在任務真正執行時：
    - 下游接收的不是上游函式本身，而是其執行結果（經由 XCom 傳遞）。
    """

    # -- 節點一：產生一個數值 ------------------------------------------------
    @task
    def produce() -> int:
        """回傳整數 1，作為下游的輸入來源。

        小提示：若要測試重試/告警，可在此故意 raise 例外，觀察 UI 行為。
        回傳值會自動寫入 XCom（key=return_value）。
        """
        return 1

    # -- 節點二：轉換數值 ----------------------------------------------------
    @task
    def transform(n: int) -> int:
        """接收上游的整數，做一個簡單運算後回傳。

        在 DAG 內呼叫 transform(produce())，表示建立相依關係並串接資料流。
        Airflow 會在執行階段把上游真正的輸出值餵給本任務的參數 n。
        """
        return n + 1

    # -- 節點三：消費結果（無回傳值） ----------------------------------------
    @task
    def consume() -> None:
        """單純執行副作用（例如 log、通知、檔案寫入等）。"""
        print("Hello from Airflow SDK")

    # ---- 串接依賴與資料流 --------------------------------------------------
    # 為了提高可讀性，先以中間變數接住 XComArg：
    x = produce()        # parse 階段回傳 XComArg；執行時會是整數 1
    y = transform(x)     # transform 依賴 produce，執行時 n=1 → 回傳 2

    # 以 >> 表示執行順序：右側依賴左側
    y >> consume()       # transform 完成後再執行 consume


# ---- 讓 Airflow 註冊此 DAG -----------------------------------------------
mini_pipeline()