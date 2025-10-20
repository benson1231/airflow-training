# Airflow Testing

本文介紹 Airflow 的測試機制與實務策略，包括 DAG 驗證、任務邏輯測試、模擬 XCom／變數、與 pytest 框架整合方式。

---

## 🧩 一、測試目的與層級

Airflow 測試分為三個層級：

| 層級                    | 範圍                      | 常見工具                                          |
| --------------------- | ----------------------- | --------------------------------------------- |
| **DAG 結構驗證**          | 確保 DAG 可被解析、沒有循環依賴、排程正常 | CLI、`DagBag`                                  |
| **Task 邏輯測試**         | 單一任務的業務邏輯、變數與 XCom 行為   | pytest、mock、context 模擬                        |
| **整合測試（Integration）** | 模擬整體流程或外部連線（如 DB、API）   | pytest + docker-compose + airflow testing env |

---

## 🧠 二、DAG 結構驗證

Airflow 會在啟動時載入所有 DAG，可利用 `DagBag` 進行結構驗證：

```python
from airflow.models import DagBag

def test_dag_integrity():
    dag_bag = DagBag(dag_folder="dags", include_examples=False)
    assert len(dag_bag.import_errors) == 0, f"DAG Import Errors: {dag_bag.import_errors}"
```

此測試可確認：

* DAG 無語法錯誤
* 無循環依賴（cycle）
* 所有任務能正確載入

---

## ⚙️ 三、Task 單元測試（Unit Test）

Task 的邏輯應該獨立可測，通常在函式層級撰寫測試：

```python
from airflow.models.dag import DAG
from pendulum import datetime
from my_dag import transform_data

def test_transform_data():
    dag = DAG(dag_id="demo_dag", start_date=datetime(2025,1,1))
    context = {"ti": None, "ds": "2025-10-20"}

    result = transform_data()
    assert result["status"] == "success"
```

> ✅ **建議：** Task 本身應盡量保持為純函式邏輯，不依賴 Airflow context，以便單元測試。

---

## 🔄 四、模擬 XCom 與 Variable

### 模擬 XCom

```python
from unittest.mock import Mock

def test_xcom_pull_push():
    ti = Mock()
    ti.xcom_pull.return_value = 42
    ti.xcom_push.return_value = None

    result = my_task(ti=ti)
    assert result == 84
```

### 模擬 Variable

```python
from airflow.models import Variable

def test_variable(monkeypatch):
    monkeypatch.setattr(Variable, "get", lambda key, default=None: "test-value")
    assert Variable.get("key") == "test-value"
```

---

## 🧪 五、pytest 整合

在 `tests/` 目錄中放置測試模組：

```bash
pytest tests/ --disable-warnings -v
```

可使用 fixtures 模擬 DAG context：

```python
import pytest
from airflow.models.dagrun import DagRun

@pytest.fixture
def dag_context():
    return {"ds": "2025-10-20", "execution_date": datetime(2025,10,20)}

def test_task_with_context(dag_context):
    result = example_task(**dag_context)
    assert result is not None
```

---

## 🧰 六、整合測試（Integration Test）

可在 `docker-compose` 或 Astronomer CLI 環境中進行：

```bash
astro dev start
pytest tests/integration/
```

模擬外部連線：

* 使用 `LocalExecutor` 或 `CeleryExecutor`
* 在 `.env` 設定假連線（mock DB/API）
* 搭配 pytest 的 `monkeypatch` 或 `responses` 模組攔截請求

---

## 🧭 七、最佳實踐

1. **將業務邏輯與 Airflow 分離**（task 函式應可單獨測試）
2. **DAG 驗證自動化**：在 CI 中跑 `DagBag()` 檢查
3. **Mock 外部依賴**：避免實際 API/DB 呼叫
4. **使用 fixtures**：簡化 context 或變數設定
5. **每次 commit 前跑 pytest**：確保 DAG 可載入

---

> ✅ **結論：** Airflow 測試並非只在 UI 層檢查 DAG 能否啟動，而是透過結構驗證、單元測試與整合模擬，確保工作流的正確性、可維護性與可重現性。
