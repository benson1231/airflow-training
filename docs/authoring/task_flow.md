# TaskFlow API（任務流程化 API）

**2025.10.22**

**TaskFlow API** 是 Airflow 自 2.0 版本引入的重要語法糖，讓使用者可以以 **Pythonic** 的方式撰寫 DAG 與任務（tasks），而不再需要傳統的 `PythonOperator`。它透過 **@dag** 與 **@task** 裝飾器（decorator）來封裝執行邏輯，使 DAG 定義更簡潔、可讀性更高。

---

## 🧭 一、設計理念

在傳統寫法中，每個任務必須手動建立 Operator 並指定 `task_id`、`python_callable`、依賴關係（`>>`、`<<`）。TaskFlow API 的目的，是讓這些步驟更直覺化，並自動處理 **XCom 資料傳遞** 與 **task dependency**。

TaskFlow API 提供：

* 更 Python 化的語法結構。
* 自動化的任務依賴鏈建構。
* 回傳值自動存入 XCom。
* 以函式參數直接傳遞上游輸出。

---

## 🧩 二、基本範例

```python
from airflow.sdk import dag, task
from pendulum import datetime

@dag(
    dag_id="taskflow_demo",
    description="Demonstration of TaskFlow API.",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["basic", "taskflow"],
)
def taskflow_demo():

    @task
    def extract() -> dict:
        data = {"value": 42}
        print(f"[extract] output = {data}")
        return data

    @task
    def transform(data: dict) -> int:
        result = data["value"] * 2
        print(f"[transform] doubled = {result}")
        return result

    @task
    def load(result: int):
        print(f"[load] final result = {result}")

    # 自動建立依賴關係
    load(transform(extract()))

# 註冊 DAG
taskflow_demo()
```

### ✅ 特性說明：

* `@task` 會自動將函式包裝為 Airflow Task。
* 函式回傳值自動以 XCom 傳遞至下游。
* 任務間依賴透過函式調用語法自動形成（無需手動使用 `>>`）。

---

## ⚙️ 三、等價的傳統寫法（對照）

傳統寫法需要明確建立 Operator：

```python
from airflow.operators.python import PythonOperator

def extract():
    return {"value": 42}

def transform(**context):
    val = context['ti'].xcom_pull(task_ids='extract')
    return val["value"] * 2

def load(**context):
    result = context['ti'].xcom_pull(task_ids='transform')
    print(f"[load] result = {result}")

extract_task = PythonOperator(task_id='extract', python_callable=extract, dag=dag)
transform_task = PythonOperator(task_id='transform', python_callable=transform, dag=dag)
load_task = PythonOperator(task_id='load', python_callable=load, dag=dag)

extract_task >> transform_task >> load_task
```

TaskFlow API 簡化了以上結構，尤其免除了 `xcom_pull` 的繁瑣語法。

---

## 🔁 四、進階應用

### (1) 自訂任務參數

```python
@task(retries=3, retry_delay=timedelta(minutes=5))
def fetch_data(url: str):
    print(f"Fetching from {url}")
```

### (2) 多輸入任務

```python
@task
def merge(a: int, b: int):
    return a + b

merge(task1(), task2())
```

### (3) 任務群組化

TaskFlow 可與 `@task_group` 結合，形成模組化流程。

```python
from airflow.decorators import task_group

@task_group
def etl_group():
    a = extract()
    b = transform(a)
    load(b)
```

---

## 🧠 五、常見錯誤與除錯建議

| 問題                                       | 原因                        | 解法                          |
| ---------------------------------------- | ------------------------- | --------------------------- |
| TypeError: 'XComArg' is not iterable     | 嘗試對上游回傳的 XComArg 進行不支援的操作 | 使用 `.resolve()` 或將邏輯包在下游任務內 |
| ValueError: circular dependency detected | 任務之間有遞迴呼叫                 | 檢查函式呼叫鏈，避免環狀依賴              |
| 任務未出現在 UI                                | DAG 函式未在底部呼叫              | 確保有執行 `my_dag()`            |

---

## 💡 六、最佳實踐

✅ 建議：

* 每個 DAG 僅保留一個 `@dag()` 函式作為主體。
* 使用 TaskFlow API 時，盡量避免在任務外部傳遞資料。
* 將共用參數以 `Variable.get()` 或 Connection 設定管理。
* 所有任務都應回傳「可序列化（JSON-serializable）」資料類型。

⚠️ 避免：

* 在 DAG 區塊外呼叫任務（會報錯）。
* 使用未封裝的全域變數傳遞資料。
* 在任務函式內進行阻塞式長時間任務，應交由 Worker 處理非同步任務。

---

> ✅ **總結**：TaskFlow API 讓 Airflow 的 DAG 更像一般 Python 程式邏輯，實現「任務＝函式、依賴＝呼叫」的自然對映，大幅簡化 DAG 結構與資
