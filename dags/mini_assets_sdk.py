"""
mini_assets_sdk.py — 使用 Airflow SDK 的 @asset 範例（詳細中文註解）

目的：
- 說明何謂「資產 (asset)」與如何定義上下游資產之間的依賴關係。
- 展示使用 @asset decorator 取代傳統 @task 的場景：當你想關注「資料物件」而非「步驟」。

重點：
1️⃣ asset 是一種「資料節點」，代表可追蹤的資料產出物，例如：API 回應、資料表、報表或模型檔案。
2️⃣ 每個 asset 都能標註 metadata（描述、標籤、URI 等），方便在 UI 或 lineage 圖上追蹤。
3️⃣ schedule 可是固定頻率（@daily），也可讓下游以上游 asset 作為觸發條件。
"""

# ---- 匯入 ---------------------------------------------------------------
from airflow.sdk import asset  # Airflow SDK 提供的 asset decorator


# ---- 上游資產：user_profile ----------------------------------------------
@asset(
    schedule="@daily",  # 每天 materialize 一次此資產
    uri="https://randomuser.me/api/",  # 外部資料來源，僅作為 metadata 標註（不自動抓取）
    tags=["api", "user"],  # 分類標籤，有助於在 UI 中篩選
    description="Fetch random user profile from API for demonstration.",
)
def user_profile() -> None:
    """此資產代表『隨機使用者基本資料』。

    實務用途：
    - 呼叫外部 API 抓取使用者 JSON 資料。
    - 寫入資料庫或保存於檔案系統中供下游分析。
    - 回傳值可為檔案路徑、資料框架或 None（僅副作用）。
    
    示範僅以列印表示動作，未做實際 API 請求。
    """
    print("[user_profile] Fetching user data from randomuser.me ... (demo only)")


# ---- 下游資產：user_geo_info --------------------------------------------
@asset(
    schedule=user_profile,  # 指定上游 asset 作為觸發條件，等 user_profile 完成後再執行
    tags=["api", "geo"],  # 與主題相關的標籤
    description="Extract geographic info from user profile asset.",
)
def user_geo_info() -> None:
    """此資產代表『由使用者資料推導出的地理資訊』。

    常見場景：
    1. 上游產出原始資料（raw data），下游依該資料生成特徵或報表。
    2. 透過共享儲存區（檔案、資料表）存取上游結果，而非直接傳遞物件。

    注意：asset 間通常不使用 XCom 傳遞資料，而是藉由外部儲存位置串接。
    本範例僅以 print 表示動作。
    """
    print("[user_geo_info] Downstream of user_profile; deriving location info ... (demo only)")