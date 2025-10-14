"""
example_sdk_dag.py — Airflow SDK 風格（@dag / @task）範例，含詳細註解

放置路徑：<你的專案>/dags/example_sdk_dag.py
此檔示範：
1) 使用 Airflow SDK 的 decorator API（from airflow.sdk import dag, task）
2) 三個任務 a → b → c 的資料/依賴關係
3) schedule 與 start_date 的基本觀念

⚠️ 提醒：
- Airflow 解析 DAG 時（scheduler / webserver parse），會執行到「宣告 DAG 與任務」的 Python 程式碼，
  但不會執行任務函式本體（函式本體只會在真正任務運行時被呼叫）。
- 本例使用 pendulum.datetime 物件作為 start_date，比 Python 的 datetime 更好處理時區。
"""

# ---- 匯入套件 --------------------------------------------------------------
# Airflow SDK 的 decorator 入口（新版 SDK 路徑）。在傳統 TaskFlow API 是 from airflow.decorators import dag, task。
from airflow.sdk import dag, task

# pendulum 是 Airflow 官方建議用於處理時區/日期時間的套件
from pendulum import datetime


# ---- 宣告 DAG --------------------------------------------------------------
@dag(
    # DAG 的排程起始時間（"第一個可能的排程點"），注意不是「立刻就跑」。
    # Airflow 會以 start_date 為基準、依 schedule 計算排程點。
    # 例如 schedule="@daily"，start_date=2025-01-01，則第一個排程點為 2025-01-01 這天的排程。
    start_date=datetime(2025, 1, 1),

    # DAG 的排程頻率。@daily 代表每天一個排程點。
    # 常見字串：@once, @hourly, @daily, @weekly, @monthly, @yearly 或 cron 表達式（例如 "0 2 * * *"）。
    schedule="@daily",

    # 你也可以視需要補上下列參數（此處保留預設行為）：
    # catchup=False,          # 是否補跑 start_date 到現在之間未執行的排程點
    # default_args={...},     # owner、retries、retry_delay 等預設參數
    # tags=["example", "sdk"],
)
def my_dag():
    """DAG 本體函式：在此函式內宣告任務與依賴關係。

    重要觀念：
    - 以 @task 裝飾的函式在「DAG 解析階段」會被包裝成可排程的 Task；
      當你在 DAG 區塊內呼叫這些函式（例如 a() ），
      回傳的不是實際執行結果，而是 XComArg（任務間資料/依賴的 placeholder）。
    - 實際的 Python 函式本體只會在 Task 被真正排程並由 worker 執行時才會跑。
    """

    # -- Task A --------------------------------------------------------------
    @task
    def a() -> int:
        """示範第一個任務：回傳整數 1。

        - 若你故意要測試錯誤重試/告警，可解除下一行 raise。
        - 任務回傳值（此處是 int 1）會經由 XCom 傳遞給下游任務。
        """
        # raise ValueError("This is a test error")  # ← 測試錯誤時可打開
        return 1

    # -- Task B --------------------------------------------------------------
    @task
    def b(x: int) -> int:
        """示範第二個任務：接收上游的數值 x，回傳 x + 1。

        - 當你在 DAG 內呼叫 b(a()) 時，實務上是將 A 的 XComArg 當作 B 的輸入；
          於執行階段，Airflow 會把 A 的實際輸出拉出來餵給 B。
        """
        return x + 1

    # -- Task C --------------------------------------------------------------
    @task
    def c() -> None:
        """示範第三個任務：不回傳資料，僅做 print 等副作用操作。"""
        print("Hello")

    # ---- 宣告依賴關係與資料流 --------------------------------------------
    # 一般可讀性較高的寫法：
    a_result = a()          # 呼叫任務 a，回傳 XComArg（非真正的數值 1，在 parse 階段只是占位符）
    b_result = b(a_result)  # b 依賴 a；執行時 b 會拿到 a 的真實回傳值（1），並回傳 2

    # 以位移運算子 >> 建立依賴（右邊依賴左邊）
    # 這裡代表：b 完成後再執行 c
    b_result >> c()


# ---- 讓 Airflow 在匯入時註冊這個 DAG --------------------------------------
# 對於 decorator 風格，必須在模組層級呼叫 DAG 函式一次，讓 DAG 物件被建立並可被解析。
my_dag()
