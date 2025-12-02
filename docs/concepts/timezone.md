# Airflow Timezone

**2025.10.22**

## 🕒 為何要設定時區（Timezone）

Airflow 的所有 DAG 執行（DAG runs）、任務排程（task scheduling）與 UI 顯示時間都受到 **timezone 設定** 影響。若未設定，預設採用 **UTC 時區**。這可能導致與實際地區時間（如台北 GMT+8）不一致，尤其在：

* DAG 的 `start_date`、`schedule` 解讀錯誤
* Web UI 顯示時間與系統時間不同
* Trigger / Sensor 依賴時間時出現偏移

---

## ⚙️ 全域設定方式

在 `airflow.cfg` 中可修改全域時區：

```ini
[core]
default_timezone = Asia/Taipei
```

> 預設為 `utc`，若設定為 `system`，則會使用系統時區。

---

## 🧩 DAG 層級設定

每個 DAG 也可在宣告時明確指定時區：

```python
from airflow import DAG
from pendulum import timezone
from datetime import datetime

tz = timezone("Asia/Taipei")

with DAG(
    dag_id="example_tz_dag",
    start_date=datetime(2025, 1, 1, tzinfo=tz),
    schedule="0 8 * * *",  # 每天早上 8 點（台北時間）
    catchup=False,
) as dag:
    ...
```

> 若 DAG 未明確指定 `tzinfo`，Airflow 會 fallback 到 `airflow.cfg` 的 `default_timezone`。

---

## 🧠 常見錯誤與對應

| 問題                           | 原因                                      | 解法                                                 |
| ---------------------------- | --------------------------------------- | -------------------------------------------------- |
| DAG 在非預期時間觸發                 | `start_date` 未加時區資訊                     | 使用 `datetime(..., tzinfo=timezone('Asia/Taipei'))` |
| Web UI 顯示 UTC 時間             | 未修改 `default_timezone` 或未啟用 Web UI 時區設定 | 調整 `airflow.cfg` 或 UI 偏好設定                         |
| TriggerDagRunOperator 觸發時間錯誤 | 上游 DAG 與下游 DAG 使用不同時區                   | 保持 DAG 時區一致                                        |

---

## 📘 建議實務

1. **明確指定 DAG 時區** — 使用 `pendulum.timezone('Asia/Taipei')`。
2. **統一整個專案時區** — 避免混用 UTC 與地區時區。
3. **記錄時間戳（timestamp）時以 UTC 儲存**，但在顯示層（UI/報表）轉換為當地時區。
4. **測試排程偏移**：以 `airflow dags next-execution <dag_id>` 驗證下一次排程時間。

---

## 🔍 延伸工具

* `pendulum`：Airflow 內建的 timezone 物件（比 `datetime.tzinfo` 更穩定）
* CLI 測試時區：

  ```bash
  airflow dags next-execution example_tz_dag
  airflow dags list-runs -d example_tz_dag
  ```
* Web UI：`User` 區塊可切換顯示時區

---

✅ **重點總結**：

* Airflow 預設使用 UTC。
* 實務上建議在 `airflow.cfg` 或 DAG 層級統一設定地區時區。
* 永遠確認 `start_date` 與 schedule 的時間對應實際期望。
