# Astro CLI

**2025.10.20**

## 一、什麼是 Astronomer CLI？

[Astronomer CLI（Astro CLI）](https://www.astronomer.io/docs/astro/cli/overview) 是一個命令列工具，用於在本地端或雲端管理、部署與操作 **Apache Airflow** 專案。它由 **Astronomer.io** 提供，旨在簡化 Airflow 的開發、測試與 CI/CD 整合流程。

CLI 可用於：

* 建立並啟動 Airflow 專案的本地開發環境。
* 管理 DAG、環境變數、Provider 套件。
* 連接並部署至 Astronomer 雲端平台。

---

## 二、Astro CLI 的主要用途

| 類別         | 功能說明                 | 範例命令                                  |
| ---------- | -------------------- | ------------------------------------- |
| **本地開發**   | 啟動本地 Airflow 環境      | `astro dev start`                     |
| **環境管理**   | 查看、停止或重啟容器           | `astro dev stop`, `astro dev restart` |
| **部署管理**   | 部署專案至 Astronomer 雲端  | `astro deploy`                        |
| **專案初始化**  | 建立新的 Astronomer 專案結構 | `astro dev init`                      |
| **DAG 測試** | 在本地測試單一 DAG 執行       | `astro dev run <dag_id>`              |
| **登入與認證**  | 登入 Astronomer 平台帳號   | `astro login`                         |
| **版本檢查**   | 顯示 CLI 與 Airflow 版本  | `astro version`                       |

---

## 三、Astro 專案結構

執行 `astro dev init` 後，CLI 會建立一個標準化的 Airflow 專案目錄：

```
my-astro-project/
├── dags/                # DAG 定義檔案
├── include/             # 輔助模組與參數
├── plugins/             # Airflow 外掛
├── requirements.txt     # Python 依賴（包含 Providers）
├── Dockerfile           # 可自訂容器環境
├── .astro/              # Astronomer 專案設定（自動生成）
└── airflow_settings.yaml # （選用）環境變數與連線設定
```

---

## 四、本地開發常用命令

| 命令                                      | 功能                                                      |
| --------------------------------------- | ------------------------------------------------------- |
| `astro dev start`                       | 啟動完整 Airflow 環境（webserver、scheduler、triggerer、postgres） |
| `astro dev stop`                        | 停止所有相關容器                                                |
| `astro dev restart`                     | 重新啟動容器並載入最新變更                                           |
| `astro dev logs`                        | 查看 Airflow 容器日誌                                         |
| `astro dev ps`                          | 顯示目前執行的容器狀態                                             |
| `astro dev kill`                        | 強制刪除所有容器與網路資源                                           |
| `astro dev parse`                       | 測試 DAG 是否能正確解析（驗證語法與依賴關係）                               |
| `astro dev pytest`                      | 執行單元測試與整合測試（使用 pytest）                                  |
| `astro dev upgrade-test`                | 檢查專案在 Astronomer CLI 升級後的相容性                            |
| `astro dev upgrade-test --version-test` | 驗證 Astronomer CLI 版本升級是否兼容                              |
| `astro dev upgrade-test --dag-test`     | 驗證所有 DAG 能否在新版 Airflow 正常運行                             |

---

## 五、`astro dev run <airflow-cli-command>` 指令說明

`astro dev run` 是 Astronomer CLI 中一個極為實用的命令，
用來在本地 Astronomer 開發環境中直接執行任何 **Airflow CLI 指令**。
它的格式為：

```bash
astro dev run <airflow-cli-command>
```

例如

```bash
astro dev run providers list
```

### 🧩 核心概念

此命令的作用相當於：

> 進入本地 Airflow 容器 → 執行你想要的 `airflow` 子命令 → 返回結果

換句話說，它讓你**不必手動進入容器**（`docker exec -it ...`），即可執行所有 Airflow 指令。

---

## 六、整合 `requirements.txt`

在 Astronomer 專案中，只需將外部套件（例如 Airflow Provider 或自訂函式庫）寫入 `requirements.txt`，CLI 會在建構時自動安裝：

```
apache-airflow-providers-slack
apache-airflow-providers-google
requests
pandas
```

CLI 建構流程：

1. 讀取 `Dockerfile`（若存在）與 `requirements.txt`。
2. 自動建立 Docker Compose 環境。
3. 啟動 Airflow webserver、scheduler、triggerer。

---

## 七、部署至 Astronomer Cloud

若使用 Astronomer 雲端服務，可透過以下步驟部署專案：

```bash
astro login            # 登入 Astronomer 帳號
astro deploy           # 部署專案至指定 workspace
```

CLI 會自動將本地 DAG、需求套件與設定上傳至對應的 Airflow 環境。

---

## 八、CLI 與 Docker Compose 的關係

Astro CLI 實際上基於 **Docker Compose** 運作，主要差異是：

* Astro CLI 自動化了 Compose 設定與容器協調。
* 提供更友好的 `astro dev` 指令集合。
* 整合 Airflow 版本、Provider 與 Astronomer 平台設定。

> 💡 **提示：** 你仍可進入 `.astro/config.yaml` 或 `Dockerfile` 自行修改環境細節，例如 Python 版本或套件來源。

---

## 九、檢查 CLI 狀態與版本

```bash
astro version
```

範例輸出：

```
Astro CLI Version: 1.22.0
Airflow Version: 2.9.2
Runtime Version: 9.0.0
```

若 CLI 出現異常，可使用：

```bash
astro dev kill && astro dev start
```

以重建乾淨的本地開發環境。

---

## 十、官方文件與資源

* 🔗 Astronomer 官方 CLI 文件：[https://www.astronomer.io/docs/astro/cli/overview](https://www.astronomer.io/docs/astro/cli/overview)
* 📦 Astronomer Provider Registry：[https://registry.astronomer.io/providers](https://registry.astronomer.io/providers)
* 🧰 GitHub 原始碼倉庫：[https://github.com/astronomer/astro-cli](https://github.com/astronomer/astro-cli)

---

### ✅ 總結

Astro CLI 讓 Airflow 的開發與部署更加模組化與自動化：

* 透過 `astro dev start` 快速啟動本地環境。
* 整合 Docker Compose、Providers 與 Cloud 部署。
* 是現代化 Airflow 專案開發的核心工具之一。
