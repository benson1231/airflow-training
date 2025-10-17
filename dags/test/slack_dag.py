from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pytz


def send_slack_message():
    slack_token = Variable.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)

    tz = pytz.timezone("Asia/Taipei")
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    message_text = f"🚀 Airflow job completed successfully at {current_time}! Nice! <!channel>"

    try:
        response = client.chat_postMessage(
            channel="#dev",
            text=message_text
        )
        print("✅ Message sent: ", response["ts"])
    except SlackApiError as e:
        print("❌ Error sending message:", e.response["error"])


with DAG(
    dag_id="send_slack_message_dag",
    start_date=datetime(2025, 10, 17),
    schedule=None,
    catchup=False,
    tags=["slack"],
) as dag:
    send_message = PythonOperator(
        task_id="send_slack",
        python_callable=send_slack_message,
    )
