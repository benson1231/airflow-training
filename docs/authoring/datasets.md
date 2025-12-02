# Datasets in Airflow

**2025.10.22**

## 🧩 概念說明

`Dataset` 是 Airflow 2.4 引入的核心功能，用於在**不同 DAG 之間**建立「資料相依性 (data dependencies)」。與傳統的任務層級依賴 (`task dependencies`) 不同，Datasets 讓你能以**資料更新事件**來觸發下游流程，而非僅依據排程時間。

換句話說，Dataset 讓 Airflow 從「時間導向 (time-based scheduling)」進化為「資料導向 (data-driven scheduling)」。

---

## 🧠 基本概念

* **Dataset 定義**：使用 `Dataset(uri)` 物件定義一個資料集，通常代表檔案、表格、資料庫或任意可辨識的資源。
* **Producer DAG**：負責更新或產生 Dataset 的 DAG。
* **Consumer DAG**：當 Dataset 被更新時自動觸發的 DAG。

---

## 🧱 定義 Dataset

```python
from airflow import Dataset

# 定義一個資料集，例如儲存在 S3 或本地的 CSV 檔案
my_dataset = Dataset("s3://data/processed/customers.csv")
```

---

## 🚀 建立 Producer 與 Consumer

```python
from airflow import DAG
from airflow.decorators import task
from datetime import datetime

# (1) Producer DAG: 更新 dataset
@dag(schedule="@daily", start_date=datetime(2024,1,1), catchup=False)
def producer_dag():
    @task(outlets=[my_dataset])
    def generate_data():
        print("Writing customers.csv ...")

    generate_data()

# (2) Consumer DAG: 監聽 dataset 更新事件
@dag(schedule=[my_dataset], start_date=datetime(2024,1,1), catchup=False)
def consumer_dag():
    @task
    def analyze_data():
        print("Triggered because customers.csv was updated!")

    analyze_data()
```

此範例中，當 `producer_dag` 更新 `customers.csv` 時，Airflow 會自動觸發 `consumer_dag`。

---

## 🧩 多重 Dataset 監聽

可讓下游 DAG 監聽多個 Dataset，只要任一資料集被更新即觸發：

```python
from airflow import Dataset

customers = Dataset("s3://data/customers.csv")
orders = Dataset("s3://data/orders.csv")

@dag(schedule=[customers, orders], start_date=datetime(2024,1,1), catchup=False)
def downstream_dag():
    ...
```

---

## 🧭 實務建議

1. **URI 規範化**：建議使用標準化路徑（如 `s3://`、`db://`、`file://`），方便日後可視化與查詢。
2. **資料可視化**：在 Airflow UI「Datasets」頁籤可檢視 Dataset 關聯圖，包含上游/下游 DAG。
3. **命名一致性**：使用模組化命名（如 `Dataset('warehouse.sales_data')`）方便維護。
4. **混合模式**：可同時保留時間排程與 Dataset 觸發，例如：

```python
@dag(schedule=[Dataset('s3://data/orders.csv'), '@weekly'])
```

---

## ⚙️ 限制與注意事項

* Dataset 僅支援 DAG 層級觸發，無法直接綁定至單一任務。
* 不支援跨環境（不同 Airflow instance）的資料觸發。
* 若上游 DAG 失敗或跳過任務，Dataset 不會被更新。

---

## ✅ 小結

| 概念               | 說明                   |
| ---------------- | -------------------- |
| **Dataset**      | 代表一個資料資源（檔案、表格、資料庫等） |
| **Producer DAG** | 負責更新 Dataset         |
| **Consumer DAG** | 被 Dataset 更新事件觸發     |
| **用途**           | 建立 DAG 間的資料驅動相依性     |

---

## 📘 延伸閱讀

* [Airflow Datasets 官方文件](https://airflow.apache.org/docs/apache-airflow/stable/concepts/datasets.html)
* [Airflow Summit 2023: Data-Aware Scheduling 介紹影片](https://www.youtube.com/watch?v=UDRQxnpdK1E)
