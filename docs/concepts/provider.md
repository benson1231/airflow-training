# Airflow Provider 模組說明

**2025.10.20**

## 一、什麼是 Provider？

在 Airflow 架構中，**Provider** 是一種**擴充套件 (Extension Package)**，用於連接外部系統、服務或資料來源。它們讓 Airflow 能夠整合各種平台，如 AWS、GCP、Slack、PostgreSQL、Snowflake、Databricks 等。

Provider 並非單純的 plug-in，而是透過 [Airflow 官方 Provider Framework](https://registry.astronomer.io/providers) 註冊的獨立模組，負責：

* 提供 Operators、Sensors、Hooks、Connections 的實作。
* 定義與外部系統的互動邏輯。
* 透過 entrypoint 機制自動載入並整合至 Airflow UI。

---

## 二、Provider 的組成結構

典型的 Provider 套件（例如 `apache-airflow-providers-google`）包含以下主要元件：

| 模組名稱                        | 功能                    | 範例                                                |
| --------------------------- | --------------------- | ------------------------------------------------- |
| **Operators**               | 定義執行特定動作的任務邏輯         | `GCSCreateBucketOperator`, `SlackAPIPostOperator` |
| **Hooks**                   | 提供與外部 API / DB 的連線邏輯  | `S3Hook`, `PostgresHook`                          |
| **Sensors**                 | 持續監測事件是否發生，用於條件觸發     | `FileSensor`, `ExternalTaskSensor`                |
| **Connections**             | 管理外部系統的連線設定（透過 UI 設定） | `aws_default`, `slack_default`                    |
| **Transfers**               | 定義兩個系統之間的資料搬移         | `S3ToRedshiftOperator`                            |
| **Secrets / Auth Backends** | 提供安全存取外部憑證的機制         | `AWS Secrets Manager`, `HashiCorp Vault`          |

---

## 三、在 Astro CLI 中安裝 Provider

在使用 Astronomer 平台開發時，你只需在 `requirements.txt` 檔案中列出所需的 Provider 套件，然後執行：

```bash
astro dev start
```

Astronomer 會在容器建構時自動安裝這些套件，無需額外修改 Dockerfile。

**範例：**

```
# requirements.txt
apache-airflow-providers-slack
apache-airflow-providers-google
apache-airflow-providers-postgres
```

執行後，這些 Provider 將自動註冊進 Airflow 環境。

---

## 四、查看已安裝 Provider

在 Airflow UI 中：

* 導覽列 → **Admin → Providers** 可查看所有已註冊 provider。
* 每個 provider 會顯示其版本、維護者、對應的 Operators 與 Hooks 清單。

或透過 CLI：

```bash
airflow providers list
```

---

## 五、Provider、Hook、Operator 的互動關係

Provider 內的元件關係如下：

```
Connection → Hook → Operator
```

* **Connection**：儲存外部系統連線資訊（帳號、密碼、API token）。
* **Hook**：負責建立與外部系統的實際連線。
* **Operator**：呼叫 Hook 執行具體任務（例如傳送訊息、查詢資料）。

**範例：**

```python
from airflow.providers.slack.operators.slack_api import SlackAPIPostOperator

slack_task = SlackAPIPostOperator(
    task_id="notify_slack",
    text="DAG Execution Completed ✅",
    channel="#data-pipeline",
)
```

在此範例中，`SlackAPIPostOperator` 背後實際使用 `SlackHook` 與 Slack API 溝通，並透過 `slack_default` Connection 載入 token。

---

## 六、自訂 Provider

若需支援內部系統（例如公司專用 API 或內部資料庫），可建立自訂 Provider：

1. 建立自訂 Hook（繼承自 `BaseHook`）。
2. 實作自訂 Operator（繼承自 `BaseOperator`）。
3. 在 `setup.cfg` 註冊 entrypoint，例如：

```ini
[options.entry_points]
airflow.providers =
    mycompany = mycompany_airflow_provider
```

4. 安裝後 Airflow 即會自動載入 `mycompany` Provider。

---

## 七、總結

* **Provider 是 Airflow 的外部整合層**，讓 DAG 能夠安全、模組化地與第三方平台互動。
* **在 Astronomer 專案中**，直接在 `requirements.txt` 列出 Provider 並執行 `astro dev start` 即可自動安裝。
* **官方 Provider 清單** 可於 Astronomer Registry 查閱：[registry.astronomer.io/providers](https://registry.astronomer.io/providers)

> ✅ **一句話總結：** Provider 是 Airflow 與外部世界的橋樑，負責讓 DAG 任務能夠安全地「說不同系統的語言」。
