# Airflow 動態任務映射 (Dynamic Task Mapping)

**2025.10.22**

## 🌭 一、概念簡介

[Dynamic Task Mapping](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html) 是 Airflow 2.3 之後引入的功能，用於 **在執行期間根據輸入資料動態建立任務實例 (task instances)**。
傳統 DAG 需要在撰寫時明確定義所有任務；但若處理多組輸入資料（如多個檔案、樣本或 API 呼叫），就需要寫大量重複的 task。
動態映射讓你根據上游輸出，**自動展開多個相同任務實例**，實現類似「for 迴圈」的效果。

---

## ⚙️ 二、原理與運作流程

1. **定義上游輸出**  上游任務回傳一個 list 或 dictionary，Airflow 會將其轉為「映射輸入」。
2. **下游任務標記為映射任務 (mapped task)**  下游任務呼叫時使用 `.expand()` 方法。
3. **執行時展開 (runtime expansion)**  Scheduler 會在 DAG Run 解析階段自動展開多個子任務實例，每個執行一組輸入。

---

## 💡 三、範例

```python
from airflow.sdk import dag, task

@dag(
    description="Demonstrate Dynamic Task Mapping in Airflow SDK.",
    tags=["advanced", "mapping"],
)
def dynamic_mapping_demo():
    @task
    def list_files() -> list[str]:
        return ["sample_a.fastq", "sample_b.fastq", "sample_c.fastq"]

    @task
    def process_file(filename: str):
        print(f"[process_file] Processing {filename} ...")

    files = list_files()
    process_file.expand(filename=files)

dynamic_mapping_demo()
```

| Task ID           | Input (`filename`) |
| ----------------- | ------------------ |
| `process_file[0]` | `sample_a.fastq`   |
| `process_file[1]` | `sample_b.fastq`   |
| `process_file[2]` | `sample_c.fastq`   |

Airflow 會自動生成對應數量的任務實例，每個可獨立執行、重試與記錄。

---

## 🧮 四、支援的資料類型

| 類型        | 說明                             |
| --------- | ------------------------------ |
| `list`    | 最常見，依序展開每個元素為一個任務。             |
| `dict`    | 鍵值對會自動展開成多個子任務。                |
| `XComArg` | 若上游輸出為 list/dict，會自動轉換為可映射的輸入。 |

---

## 🛠️ 五、進階用法

### 1️⃣ 多參數映射

```python
process_pair.expand(file=files, sample_id=ids)
```

### 2️⃣ partial 固定部分參數

```python
process_file.partial(mode="fastq").expand(filename=files)
```

### 3️⃣ 動態收合

可利用 `@task(multiple_outputs=True)` 或額外的彙總任務彙整結果。

---

## 🧠 六、for 迴圈 vs Dynamic Mapping

| 項目       | for 迴圈   | Dynamic Mapping  |
| -------- | -------- | ---------------- |
| 任務生成時機   | DAG 定義階段 | DAG 執行階段         |
| 是否顯示於 UI | 否        | 是                |
| 平行化能力    | 單執行序     | 可由 Executor 平行運行 |
| 錯誤恢復     | 不支援個別重試  | 每個子任務可獨立重試       |

---

## 🔍 七、實務應用

* 批次處理多個資料檔案（RNA-seq、影像、報表）
* 多組樣本同時執行 QC 或分析 pipeline
* 對多個 API endpoint 發送平行請求

---

## ✅ 八、最佳實踐

* 輸出清單建議不超過上百項，避免 Scheduler 壓力。
* 超過 1000 筆改用外部資料庫或批次分段處理。
* 避免 nested mapping；可搭配 TaskGroup 維持 DAG 結構。

---

> **總結**：Dynamic Task Mapping 讓 Airflow 具備「資料驅動的動態任務生成能力」，能根據輸入自動擴展平行任務，是實現高可擴展 ETL 與 NGS 批次處理的重要功能。
