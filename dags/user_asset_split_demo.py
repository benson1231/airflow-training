"""
user_asset_split_demo.py — Airflow SDK 資產（Asset）示範：單一上游、多個下游資產分別定義

功能概要：
- 利用 @asset 定義一個上游資產（user_profile）與兩個下游資產（user_geo、user_auth）。
- 展示資產之間的依賴關係（下游 schedule=user_profile）。
- 透過 XCom 讀取上游回傳值作為教學用途（實務上建議改為外部儲存銜接）。

注意事項：
⚠️ 在資產導向流程裡，建議把上游結果寫到外部儲存（檔案/表格/S3 等），
再由下游讀取。XCom 適合小量暫存、除錯示範。
"""

# ---- 匯入 -----------------------------------------------------------------
from airflow.sdk import asset, Asset, Context


# ---- 上游資產：user_profile ----------------------------------------------
@asset(
    schedule="@daily",                   # 每天 materialize 一次
    uri="https://randomuser.me/api/",   # 外部 API 來源（僅 metadata，非自動抓取）
    tags=["api", "user"],               # 標籤方便在 UI 篩選或 lineage 視圖
    description="Fetch a random user JSON payload from RandomUser API.",
)
def user_profile(context: Context) -> dict:
    """呼叫 RandomUser API 並回傳 JSON。

    參數：
        context (Context): Airflow 執行上下文，可由 context['ti'] 取得 TaskInstance。

    回傳：
        dict: 完整的 API JSON（預期包含 'results' 陣列）。

    行為說明：
    - decorator 的 `uri` 僅作為資產的描述性欄位（metadata），不會自動發請求。
    - 這裡用 requests 呼叫 API；res.raise_for_status() 能在非 2xx 時拋出例外，
      讓任務失敗以利 Airflow 重試/告警。
    - 函式回傳值會由 SDK 自動放入 XCom，供下游示範拉取。
    """
    import requests

    api = "https://randomuser.me/api/"
    print(f"[user_profile] Fetching from {api}")

    res = requests.get(api, timeout=10)
    res.raise_for_status()  # 非 2xx → 拋例外

    data = res.json()
    print(f"[user_profile] Received keys: {list(data.keys())}")
    return data


# ---- 下游資產 1：user_geo -------------------------------------------------
@asset(
    schedule=user_profile,  # 依賴上游 user_profile 完成後再 materialize
    tags=["derived", "geo"],
    description="Extract geographic information from the user_profile payload.",
)
def user_geo(user_profile: Asset, context: Context) -> dict:
    """從上游 JSON 中提取地理資訊（location）。

    步驟：
    1) 透過 XCom 拉取上游 user_profile 的回傳值。
    2) 解析 data['results'][0]['location']。
    3) 回傳 location 字典；此回傳值將作為 user_geo 資產的 materialization 內容。

    提醒：
    - asset 模式建議改以外部儲存共享資料；這裡以 XCom 作為教學示例。
    - `dag_id` / `task_ids` 使用 `user_profile.name`，避免找不到資產名稱（ASSET_NOT_FOUND）。
    """
    ti = context["ti"]

    payload = ti.xcom_pull(
        dag_id=user_profile.name,
        task_ids=user_profile.name,
        include_prior_dates=True,  # 若本次沒有，允許取用上一次的成功結果
    )

    if not payload:
        raise ValueError("No upstream user_profile data available.")

    location = payload["results"][0]["location"]
    print(f"[user_geo] location keys preview: {list(location.keys())[:3]}")
    return location


# ---- 下游資產 2：user_auth -----------------------------------------------
@asset(
    schedule=user_profile,  # 同樣依賴上游 user_profile
    tags=["derived", "auth"],
    description="Extract login credentials from the user_profile payload.",
)
def user_auth(user_profile: Asset, context: Context) -> dict:
    """從上游 JSON 中提取登入資訊（login）。

    步驟：
    1) 透過 XCom 拉取上游 user_profile 的回傳值。
    2) 解析 data['results'][0]['login']。
    3) 回傳 login 字典；此回傳值將作為 user_auth 資產的 materialization 內容。

    實務建議：
    - 若下游需要與其他系統共享資料，建議上游寫入共享儲存（如 S3/GCS/DB），
      下游再讀取該來源；這樣更符合 asset/data product 的精神。
    """
    ti = context["ti"]

    payload = ti.xcom_pull(
        dag_id=user_profile.name,
        task_ids=user_profile.name,
        include_prior_dates=True,
    )

    if not payload:
        raise ValueError("No upstream user_profile data available.")

    login = payload["results"][0]["login"]
    print(f"[user_auth] login keys preview: {list(login.keys())[:3]}")
    return login