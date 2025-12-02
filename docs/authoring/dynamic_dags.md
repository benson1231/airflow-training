# Dynamic DAGs（動態 DAG 生成）

**2025.10.22**

---

## 🧩 一、概念說明

在 Airflow 中，[Dynamic DAGs](https://airflow.apache.org/docs/apache-airflow/stable/howto/dynamic-dag-generation.html)（動態 DAG）指的是：在 DAG 解析階段（parse time）動態生成多個 DAG 或任務結構，而非手動逐一定義。這種方式常用於：

* 多資料來源自動化導入（e.g., 每個客戶一個 DAG）
* 批次任務自動配置（e.g., 每個表格或檔案自動建立 ETL 流程）
* 參數化實驗（e.g., 各種 model 設定自動展開為獨立 DAG）

Dynamic DAGs 的設計理念是「讓程式自動生成 DAG 結構」，提高彈性與可維護性。

---

## ⚙️ 二、運作原理

Airflow 會在 **Scheduler 掃描 DAG 檔案時** 執行 Python 程式碼，將每個 `DAG` 實例化並載入。若在這個階段動態建立 DAG（例如用迴圈），系統會為每個產生的 DAG 註冊獨立的 `dag_id`。

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# ---- 定義資料來源 ---------------------------------------------------
datasets = ["customer_a", "customer_b", "customer_c"]

# ---- 動態產生多個 DAG ----------------------------------------------
for name in datasets:
    dag_id = f"etl_{name}"

    with DAG(
        dag_id=dag_id,
        start_date=datetime(2025, 1, 1),
        schedule="@daily",
        catchup=False,
        tags=["dynamic", name],
    ) as dag:

        def etl_task():
            print(f"Running ETL for {name}")

        run = PythonOperator(
            task_id="run_etl",
            python_callable=etl_task,
        )

    globals()[dag_id] = dag  # ✅ 向 Airflow 註冊 DAG
```

📘 **關鍵重點：**

* `globals()[dag_id] = dag` 是關鍵步驟：讓 Airflow 識別這些動態產生的 DAG。
* 每個 `dag_id` 必須唯一。
* DAG 結構應固定（parse time 可確定），避免 runtime 產生變化。

---

## 🧠 三、常見應用場景

| 類型         | 說明                               |
| ---------- | -------------------------------- |
| 🔹 多客戶 ETL | 根據資料庫表或 API 名單自動建立 DAG，每個客戶一條管線。 |
| 🔹 多實驗參數   | 自動為不同參數組合（如模型設定）生成獨立 DAG。        |
| 🔹 檔案監控    | 偵測到新檔案（如每日上傳 CSV）即自動建立對應任務。      |

---

## 🧩 四、與 Dynamic Task Mapping 的差異

| 特徵   | Dynamic DAGs | Dynamic Task Mapping |
| ---- | ------------ | -------------------- |
| 層級   | 生成多個 DAG     | 生成單一 DAG 內多個任務       |
| 時間點  | parse time   | runtime（執行階段）        |
| 用途   | 自動建立多條獨立工作流  | 同一 DAG 中依輸入展開多任務     |
| 優勢   | 清楚分離、易於監控    | 不必創建多個 DAG、邏輯集中      |
| 適用場景 | 多資料來源、專案隔離   | 批次處理、多輸入參數展開         |

---

## 💡 五、最佳實踐

✅ **建議做法：**

* 在動態生成前，確認輸入資料（例如 `datasets`）是固定可列舉的。
* 將 DAG 生成邏輯封裝成函式，避免解析時重複運算。
* 加入錯誤處理與日誌，確保每個 DAG 初始化成功。
* 使用 `tags` 標記來源，以利後續篩選與維護。

⚠️ **避免問題：**

* 不要在 DAG parse 階段進行網路請求或讀取大型檔案（會拖慢 Scheduler）。
* 不要在 runtime 生成新的 DAG（Airflow 不支援動態 DAG hot load）。

---

## 📘 六、延伸應用

* 可結合 **外部設定檔**（如 YAML/JSON）集中管理：

```python
import json
from pathlib import Path

configs = json.loads(Path("configs.json").read_text())

for conf in configs:
    dag_id = f"etl_{conf['name']}"
    with DAG(dag_id=dag_id, schedule=conf["schedule"], start_date=datetime(2025, 1, 1)) as dag:
        ...  # 根據設定建立任務
    globals()[dag_id] = dag
```

* 或與 **Dataset-aware scheduling** 結合，讓上游更新自動觸發動態 DAG。

---

## ✅ 小結

Dynamic DAGs 讓 Airflow 能自動化生成多個工作流，是多租戶 ETL、資料整合與大規模任務管理的理想方式。其核心理念是：**在 DAG 解析階段根據輸入動態生成 DAG 結構**，以最小維護成本支援大規模自動化部署。
