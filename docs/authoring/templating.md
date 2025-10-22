# Airflow 模板化機制（Templating）

## 🧭 一、概念說明

Airflow 的 **Templating（模板化）** 機制讓你能在任務（Task）或 DAG 中動態插入變數，例如日期、檔案名稱、路徑或上游任務的輸出。
這是透過 **Jinja2 語法** 實作的，也就是在字串中使用 `{{ ... }}` 來注入變數或邏輯運算。

---

## 🧩 二、支援範圍

| 類別              | 可模板化對象                                      | 範例                                             |
| --------------- | ------------------------------------------- | ---------------------------------------------- |
| DAG 層級          | `default_args`、`params`、`schedule_interval` | `{{ ds }}`、`{{ macros.ds_add(ds, 1) }}`        |
| Operator 層級     | `bash_command`、`sql`、`op_args`、`op_kwargs`  | `echo {{ task_instance.xcom_pull('task_a') }}` |
| Hook／Connection | URL、query、路徑                                | `s3://mybucket/{{ ds }}/data.csv`              |

> ✅ 幾乎所有以字串定義的參數（例如 `bash_command`、`sql`）都可使用模板化變數。

---

## ⚙️ 三、Jinja2 模板語法

| 語法                                    | 用途           | 範例                                     |
| ------------------------------------- | ------------ | -------------------------------------- |
| `{{ variable }}`                      | 插入變數         | `{{ ds }}` → 2025-10-20                |
| `{% for i in seq %} ... {% endfor %}` | 迴圈           | 產生多個輸出                                 |
| `{% if condition %} ... {% endif %}`  | 條件邏輯         | 根據條件插入不同內容                             |
| `{{ macros.<func>() }}`               | Airflow 內建巨集 | `{{ macros.ds_add(ds, 7) }}` → 日期加 7 天 |

Airflow 預設提供的變數包括：

| 名稱                     | 說明                                     |
| ---------------------- | -------------------------------------- |
| `ds`                   | 執行日期（execution_date）YYYY-MM-DD         |
| `ts`                   | 精確時間戳記（包含時區）                           |
| `dag`、`task`           | DAG 與 Task 的物件實體                       |
| `task_instance` 或 `ti` | 當前 TaskInstance                        |
| `prev_ds`, `next_ds`   | 前／後一個排程日期                              |
| `macros`               | 內建函式（如 `ds_add`, `datetime`, `uuid` 等） |

---

## 🧪 四、範例：BashOperator 中模板化日期

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    dag_id="templating_demo",
    start_date=datetime(2025, 10, 1),
    schedule="@daily",
    catchup=False,
)

# 使用模板化變數 {{ ds }} 插入執行日期
bash_task = BashOperator(
    task_id="print_date",
    bash_command="echo Today is {{ ds }}",
    dag=dag,
)
```

**輸出範例：**

```
Today is 2025-10-20
```

---

## 🧩 五、範例：模板化 SQL 查詢

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

query = """
SELECT COUNT(*) FROM sales
WHERE date = '{{ ds }}';
"""

pg_task = PostgresOperator(
    task_id="query_sales",
    postgres_conn_id="pg_default",
    sql=query,
    dag=dag,
)
```

**說明：**

* `{{ ds }}` 在執行時會自動替換為當前 DAG Run 的執行日期。
* 這種模板化對資料查詢與報表任務特別實用。

---

## 🧠 六、自訂模板變數與巨集

若需要額外變數，可以在 DAG 中使用 `template_context` 或自訂巨集：

```python
def get_user():
    return "benson"

dag = DAG(
    dag_id="custom_template",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    user_defined_macros={"user": get_user}
)

BashOperator(
    task_id="show_user",
    bash_command="echo Current user: {{ user() }}",
    dag=dag,
)
```

**輸出：**

```
Current user: benson
```

---

## 🔍 七、模板渲染與除錯

可在 Web UI 的 **Task Instance → Rendered Templates** 查看模板渲染後的結果。

或使用 CLI 測試：

```bash
airflow tasks render my_dag_id my_task_id 2025-10-20
```

這會顯示經 Jinja 渲染後的實際內容，方便除錯。

---

## 💡 八、最佳實踐

✅ 建議：

* 使用 `{{ ds }}` 或 `macros.ds_add()` 處理日期偏移，避免手動運算。
* 將模板集中放在變數或 SQL 檔案中，提升可維護性。
* 若 SQL 複雜，可外部存 `.sql` 檔，再在 Operator 中以 `template_searchpath` 指定目錄。

⚠️ 避免：

* 在模板中執行過於複雜的邏輯（例如多層巢狀 if/for）。
* 混合 Python 與 Jinja 語法導致可讀性下降。

---

> **總結：** Airflow 的模板化機制讓 DAG 更具彈性與可重用性。善用 Jinja2 語法與 Airflow 巨集，可讓任務根據日期、上游結果或外部參數自動調整執行內容，是撰寫動態與參數
