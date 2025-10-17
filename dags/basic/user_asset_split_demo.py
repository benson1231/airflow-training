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
    import requests

    api = "https://randomuser.me/api/"
    print(f"[user_profile] Fetching from {api}")

    res = requests.get(api, timeout=10)
    res.raise_for_status()

    data = res.json()
    print(f"[user_profile] Received keys: {list(data.keys())}")
    return data


# ---- 下游資產 1：user_geo -------------------------------------------------
@asset(
    schedule=user_profile,
    tags=["derived", "geo"],
    description="Extract geographic information from the user_profile payload.",
)
def user_geo(user_profile: Asset, context: Context) -> dict:
    ti = context["ti"]

    payload = ti.xcom_pull(
        dag_id=user_profile.name,
        task_ids=user_profile.name,
        include_prior_dates=True,
    )

    if not payload:
        raise ValueError("No upstream user_profile data available.")

    # 🔧 若 payload 是 list，取出第一個元素
    if isinstance(payload, list):
        payload = payload[0]

    location = payload["results"][0]["location"]
    print(f"[user_geo] location keys preview: {list(location.keys())[:3]}")
    return location


# ---- 下游資產 2：user_auth -----------------------------------------------
@asset(
    schedule=user_profile,
    tags=["derived", "auth"],
    description="Extract login credentials from the user_profile payload.",
)
def user_auth(user_profile: Asset, context: Context) -> dict:
    ti = context["ti"]

    payload = ti.xcom_pull(
        dag_id=user_profile.name,
        task_ids=user_profile.name,
        include_prior_dates=True,
    )

    if not payload:
        raise ValueError("No upstream user_profile data available.")

    # 🔧 若 payload 是 list，取出第一個元素
    if isinstance(payload, list):
        payload = payload[0]

    login = payload["results"][0]["login"]
    print(f"[user_auth] login keys preview: {list(login.keys())[:3]}")
    return login