from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_slack_message():
    slack_token = Variable.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel="#dev",
            text="🚀 Airflow job completed successfully! Woohoo! <!channel>"
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
