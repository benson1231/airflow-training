"""
example_assets_sdk.py — 使用 Airflow SDK 的 @asset 寫法，示範兩個資產（assets）之間的相依。

放置路徑：<你的專案>/dags/example_assets_sdk.py

重點說明：
1) 什麼是 asset（資產）？
   - 可把它想成「資料產品 / 物件」的邏輯定義，例如：一份原始 API 資料、一張清理後的資料表、一個特徵檔案。
   - 每個資產有自己的 metadata（描述、標籤、URI 等），以及 materialize（實際產生/更新）的邏輯（在函式本體內）。

2) 為什麼用 @asset 而不是傳統 @task？
   - @task 強調「步驟」；@asset 強調「資料物件」。
   - 在 data lineage、觀測與 UI 展示上，@asset 對於「這份資料是由哪個上游產生」更直觀。

3) schedule 參數：
   - 可給排程字串（如 "@daily"、cron），表示此資產應以該頻率 materialize。
   - 也可讓下游資產把上游資產（asset 函式）作為 schedule 來源，表示：等上游完成後再跑（等價於建立 asset 依賴）。
     * 註：實作上等同於宣告 upstream→downstream 的關係，讓 scheduler 知道要在上游 materialize 之後觸發下游。

4) uri 參數：
   - 作為資產對應的「外部來源/目標」描述（metadata）。
   - 不等於自動抓取；是否存取該 URI 要寫在函式本體中（例如 requests.get）。

5) 回傳型別：
   - 本例示範 None，僅列印；實務上常回傳路徑、物件或將結果寫到檔案/資料庫。

6) 相依關係：
   - 下方 user_location 將 schedule 設為 user，代表「當 user 資產 materialize 完成後，再 materialize user_location」。
   - 這能對齊資料血緣（user → user_location）。
"""

# ---- 匯入 ---------------------------------------------------------------
from airflow.sdk import asset   # 新版 SDK 的 asset decorator


# ---- 定義上游資產：user -----------------------------------------------
@asset(
    schedule="@daily",                      # 每天 materialize 一次此資產（建立排程點）
    uri="https://randomuser.me/api/",      # 此資產對應的外部來源（純 metadata，不會自動抓）
    tags=["api", "user"],                  # 方便在 UI / 查詢上分類、篩選
    description="Fetches a random user from the API",  # 人類可讀的說明文字
)
def user() -> None:
    """此資產代表：『隨機使用者資料』。

    實務上你可以：
    - 以 requests/HTTP 客戶端呼叫 API
    - 將原始 JSON 存成檔案或寫入資料庫
    - 回傳檔案路徑 / 物件（或僅以副作用完成 materialize）

    注意：示範僅列印，不做實際抓取。
    """
    print("[user] Fetching user data from https://randomuser.me/api/ ... (demo only)")


# ---- 定義下游資產：user_location --------------------------------------
@asset(
    schedule=user,   # 將上游資產作為 schedule 來源 → 表示『等 user 完成後再跑我』
    tags=["api", "user"],
    description="Returns user location",   # 這裡描述此資產產生/暴露的是『使用者位置』這個資料觀點
)
def user_location() -> None:
    """此資產代表：『從 user 資產推導出使用者地理位置』。

    若要真的拿到 user 資料，有兩種常見做法：
    1) 讓 user 在 materialize 時把資料寫到檔案/表格（例如 /data/raw/user.json），
       這裡再讀該檔解析 location。
    2) 在 assets 之間用慣例的儲存位置 / 命名規則，或另行使用 task/XCom（較不建議混用）。

    在本示範中，僅列印，不做實際轉換。
    """
    print("[user_location] Downstream of 'user'; would transform to a location view (demo only)")
