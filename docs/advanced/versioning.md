# DAG Versioning（DAG 版本管理）

## 🧭 一、概念與目的

DAG Versioning 是指在 Airflow 專案中維護同一 DAG 的多個版本，以便：

1. **追蹤 DAG 改動歷史**（例如新任務、新邏輯或新參數）。
2. **允許不同版本同時存在**（例如生產版本與測試版本並行運作）。
3. **支援部署回溯**（出現錯誤時可快速回退到穩定版本）。

Airflow 3 開始引入 **DAG Bundles** 與更嚴謹的 version metadata 概念，使 DAG 版本控制更具結構化。

---

## ⚙️ 二、DAG 版本的定義方式

常見的版本標註方式有兩種：

### (1) 以 `dag_id` 命名區分

```python
@dag(
    dag_id="example_etl_v2",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "v2"]
)
def etl_v2():
    ...
```

👉 優點：簡單直觀，易於並行測試。缺點：DAG 數量多時不易統一管理。

### (2) 使用 `version` 參數或自訂變數

```python
DAG_VERSION = "v1.2"

@dag(
    dag_id=f"example_dag_{DAG_VERSION}",
    description=f"Example DAG version {DAG_VERSION}",
    start_date=datetime(2025,1,1),
    schedule="@daily",
)
def example_dag():
    ...
```

👉 優點：可統一控制 DAG 名稱與描述。便於 CI/CD 自動生成版本。

---

## 📦 三、DAG Bundles 與版本追蹤

Airflow 3.x 新增 **DAG Bundles** 機制，用於將 DAG 的程式碼、設定與依賴打包成獨立 bundle，提供：

* **版本化封裝**：每次部署生成唯一版本（含 hash 或 build id）。
* **可回溯部署**：可在 Web UI 中查看、啟用或回退舊版本。
* **一致性保證**：執行時明確綁定使用哪一版 DAG（避免部分節點使用舊邏輯）。

範例結構：

```
my_dag_project/
 ├── dags/
 │   ├── etl_dag.py
 │   └── etl_dag_bundle.yaml
 ├── requirements.txt
 └── README.md
```

在 `etl_dag_bundle.yaml` 中：

```yaml
version: v1.2.3
entrypoint: dags/etl_dag.py
metadata:
  author: benson1231
  created: 2025-10-20
```

---

## 🧩 四、DAG Versioning 與 CI/CD 整合

搭配版本控制系統（如 Git），可將 DAG version metadata 自動化：

| 組件                        | 功能                                   |
| ------------------------- | ------------------------------------ |
| **Git Tag / Commit Hash** | 作為版本來源，例如 `v1.0.3` 或 `sha-abc1234`   |
| **CI Pipeline**           | 在部署前自動寫入 `bundle.yaml` 中的 version 欄位 |
| **Airflow UI**            | 可在 DAG 詳細頁查看版本資訊與部署時間                |

範例 CI 腳本片段：

```bash
export DAG_VERSION=$(git describe --tags --always)
sed -i "s/^version:.*/version: ${DAG_VERSION}/" dags/etl_dag_bundle.yaml
astro deploy
```

---

## 📊 五、與 Dynamic DAGs 的差異

| 特性   | Dynamic DAGs    | DAG Versioning |
| ---- | --------------- | -------------- |
| 核心目的 | 根據輸入自動生成 DAG 結構 | 追蹤與管理 DAG 改版歷史 |
| 執行期間 | DAG 定義階段動態生成    | 部署階段固定化版本      |
| 常見應用 | 資料集導入、自動批次任務    | 測試與生產版本並行、回溯調試 |

---

## 💡 六、實務建議

✅ **命名規範化**：使用 `dag_id=etl_v{VERSION}` 或 `f"etl_{DATE_TAG}"`。

✅ **集中版本變數**：於專案根目錄建立 `version.py`，統一管理所有 DAG 版本。

✅ **Bundle Metadata 保留**：建議記錄作者、建立日期、依賴套件版本，提升可追溯性。

✅ **自動部署與回滾**：結合 GitHub Actions 或 Jenkins pipeline，自動部署最新 DAG bundle 並保留 N 個歷史版本。

---

> 🧠 **總結：** DAG Versioning 提供 Airflow 專案在生命週期管理上的彈性與可追蹤性，搭配 DAG Bundles 與 CI/CD，自動化維護與回滾版本可大幅提升生產穩定性與可重現性。
