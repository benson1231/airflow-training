from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import pendulum
import pytz


def fetch_weather():
    API_KEY = Variable.get("CWA_API_KEY")
    CWA_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    params = {
        "Authorization": API_KEY,
        "locationName": "臺北市",
    }

    r = requests.get(CWA_URL, params=params)
    data = r.json()

    locations = data.get("records", {}).get("location", [])
    if not locations:
        return f"❌ 找不到城市資料：{data}"

    location = locations[0]

    # 三十六小時資料有三段 time
    # 0 → 今日白天（早）
    # 1 → 今日晚上（晚）
    # 2 → 明日白天（可選）
    weather = {"early": {}, "night": {}}

    for elem in location["weatherElement"]:
        name = elem["elementName"]

        # 早（time[0]）
        if len(elem["time"]) > 0:
            weather["early"][name] = elem["time"][0]["parameter"]["parameterName"]

        # 晚（time[1]）
        if len(elem["time"]) > 1:
            weather["night"][name] = elem["time"][1]["parameter"]["parameterName"]

    # 建立 summary
    summary = f"""
🌤 **臺北市今日天氣預報**

🌅 **早（06–18）**
- 天氣：{weather['early'].get('Wx')}
- 🌧 降雨機率：{weather['early'].get('PoP')}%
- 🌡 最高溫：{weather['early'].get('MaxT')}°C
- 🌡 最低溫：{weather['early'].get('MinT')}°C
- 😌 舒適度：{weather['early'].get('CI')}

🌙 **晚（18–翌日06）**
- 天氣：{weather['night'].get('Wx')}
- 🌧 降雨機率：{weather['night'].get('PoP')}%
- 🌡 最高溫：{weather['night'].get('MaxT')}°C
- 🌡 最低溫：{weather['night'].get('MinT')}°C
- 😌 舒適度：{weather['night'].get('CI')}

資料來源：中央氣象署（36 小時預報）
"""
    return summary.strip()



def send_slack_message(**context):
    slack_token = Variable.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)

    summary = context["ti"].xcom_pull(task_ids="fetch_weather_task")

    tz = pytz.timezone("Asia/Taipei")
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M")

    message = f"📅 {now}\n{summary}"

    try:
        response = client.chat_postMessage(channel="#dev", text=message)
        print("✅ Slack message sent:", response["ts"])
    except SlackApiError as e:
        print("❌ Error sending Slack message:", e.response["error"])


# 設定 Airflow DAG Timezone（台北）
local_tz = pendulum.timezone("Asia/Taipei")

with DAG(
    dag_id="send_taipei_weather_to_slack",
    start_date=pendulum.datetime(2025, 1, 1, tz=local_tz),
    schedule="0 8 * * *",
    catchup=False,
    tags=["weather", "slack"],
) as dag:

    fetch_weather_task = PythonOperator(
        task_id="fetch_weather_task",
        python_callable=fetch_weather,
    )

    send_slack_task = PythonOperator(
        task_id="send_slack_task",
        python_callable=send_slack_message,
    )

    fetch_weather_task >> send_slack_task
