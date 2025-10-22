# Task Dependencies

本文說明 Airflow 任務之間的依賴（Dependencies）設定方法與進階用法，包括 `>>`、`<<`、`chain()` 等語法，以及在動態 DAG、TaskFlow、TaskGroup 中的實務應用。

---

## 🧭 一、依賴的基本概念（Basic Concept）

Airflow 的 DAG（Directed Acyclic Graph）代表一組**具方向性**的任務關係。每個任務（Task）都是圖中的一個節點，依賴關係則由箭頭（edges）表示任務執行順序。

```python
# 任務依賴的基本語法
start_task >> mid_task >> end_task
```

此語法表示：
- `mid_task` 在 `start_task` 成功後執行。
- `end_task` 在 `mid_task` 成功後執行。

> ✅ Airflow 僅允許「無循環依賴」，即 DAG 必須是 acyclic（無迴圈）。

---

## ⚙️ 二、依賴語法（Operators）

### 1️⃣ `>>` 與 `<<`（最常見語法）
```python
a >> b  # a 先執行，b 後執行
b << a  # 同上，反向寫法
```

### 2️⃣ 一對多與多對一
```python
# 一對多
start >> [task_a, task_b, task_c]

# 多對一
[task_a, task_b] >> end
```
> `[]` 代表任務群組，可同時建立多條依賴。

### 3️⃣ `chain()`（清晰定義線性流程）
```python
from airflow.models.baseoperator import chain
chain(start, task_a, task_b, task_c, end)
```
- 可避免重複使用 `>>`。
- 在動態 DAG 生成中（for-loop）特別常用。

### 4️⃣ `cross_downstream()`（笛卡爾依賴）
```python
from airflow.models.baseoperator import cross_downstream

cross_downstream([extract_a, extract_b], [transform_x, transform_y])
```
> 此方法建立所有上游 → 所有下游的完全對應關係。
> 等價於：`extract_a >> transform_x, transform_y` 與 `extract_b >> transform_x, transform_y`。

---

## 🧩 三、TaskFlow API 依賴（函式式任務）

在 TaskFlow API 下，每個 `@task` 函式回傳的結果會自動轉成 XComArg 物件，可直接作為參數傳遞。

```python
from airflow.decorators import dag, task
from pendulum import datetime

@dag(start_date=datetime(2025,1,1), schedule=None)
def dependency_demo():

    @task
def get_data():
        return 42

    @task
def process(value: int):
        print(f"Processed: {value}")

    # 自動建立依賴（XComArg）
    process(get_data())


dependency_demo()
```
> 當函式以另一任務的回傳值作為輸入時，Airflow 會**自動建立依賴關係**，無須手動寫 `>>`。

---

## 🧱 四、TaskGroup 內外依賴（Group Dependencies）

當任務被包在 `TaskGroup` 中時，依賴可設定在**群組與群組之間**或**群組與單一任務之間**：

```python
from airflow.decorators import dag, task, task_group

@dag(schedule=None)
def group_dependency_demo():

    @task
def start():
        pass

    @task_group
def preprocess():
        @task
def clean(): pass
        @task
def normalize(): pass
        clean() >> normalize()

    @task_group
def analysis():
        @task
def model(): pass
        @task
def visualize(): pass
        model() >> visualize()

    @task
def end():
        pass

    # 群組級依賴
    start() >> preprocess() >> analysis() >> end()

group_dependency_demo()
```
> Airflow 會自動展開群組內部的任務鏈，確保上下游連線正確。

---

## 🔁 五、動態依賴（Dynamic Dependencies）

在動態 DAG 或任務映射（Dynamic Task Mapping）中，依賴可透過變數或 for 迴圈自動生成：

```python
@task
 def subtask(num):
     print(num)

@task
 def trigger_all(nums):
     for n in nums:
         subtask.override(task_id=f"subtask_{n}")(n)

# 自動建立多條依賴
trigger_all([1,2,3])
```
> Airflow SDK 自動為每個動態生成的任務建立依賴鏈，無需人工定義。

---

## 🧠 六、依賴管理建議

| 類型 | 適用情境 | 優點 |
|------|-----------|------|
| `>>` / `<<` | 少量靜態任務 | 直觀、易讀 |
| `chain()` | 線性長流程 | 結構清晰 |
| `TaskFlow XComArg` | 需要參數傳遞 | 自動依賴、整合資料流 |
| `TaskGroup` | 模組化流程 | 層次清楚 |
| 動態依賴 | for-loop、自動化生成 | 節省代碼量 |

---

## 📘 小結

- Airflow 的依賴關係構成 DAG 的核心邏輯，確保任務正確執行順序。
- 可混合使用靜態與動態定義（例如 XComArg + chain）。
- 在大型專案中，建議使用 TaskGroup 與命名規則維持結構清晰。

> ✅ **關鍵原則**：依賴關係應反映真實資料流與邏輯順序，不應為了視覺排列而強制連線。