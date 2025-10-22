# 🚀 Airflow-Training

[![Docker Engine](https://img.shields.io/badge/Docker-27.5.1-blue?logo=docker)](https://www.docker.com/get-started/)
[![Astro CLI](https://img.shields.io/badge/Astro%20CLI-1.36.0-purple?logo=astro)]()
[![Airflow Runtime](https://img.shields.io/badge/Airflow-3.1.0%2Bastro.2-orange?logo=apache-airflow)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

---

## 🌍 Overview

This repository provides a complete and ready-to-run **Apache Airflow learning environment**.

Key features:

* Ready-to-run Airflow setup powered by **Docker** and **Astronomer CLI**.
* Includes practical **DAG examples**.
* Provides a detailed **documentation set** under [docs folder](docs/README.md), explaining Airflow concepts, operators, and advanced usage.
* Demonstrates real-world integrations such as **Slack notification** and **Postgres connections**.

---

### ⚙️ Environment

| Component | Version |
|------------|----------|
| Docker Engine | 27.5.1 |
| Astro CLI | 1.36.0 |
| Astronomer Runtime | 3.1.0 + astro.2 |

---


## 📦 Project Structure

```
AIRFLOW-TRAINING/
├── dags/                # All DAGs (organized by category)
├── include/             # Shared Python modules (utils)
├── docs/                # Markdown documentation and guides
├── .astro/              # Astronomer CLI configuration
├── Dockerfile           # Custom Airflow image definition
├── requirements.txt     # Python dependencies
├── packages.txt         # Optional Linux packages
├── docker-compose.yaml  # Docker Compose setup for Airflow
└── README.md            # This documentation
```

---

## 🧩 Requirements

You need the following installed before starting:

* **Docker:** [Get Docker](https://www.docker.com/get-started/)
* **Astronomer CLI:** [Install Astronomer CLI](https://www.astronomer.io/docs/astro/cli/install-cli)

Ensure that the **Docker daemon is running** before starting any Airflow services.

---

## ⚙️ Quick Start with Astronomer CLI

### Start Airflow environment

```bash
astro dev start
```

### Stop the environment

```bash
astro dev stop
```

### Restart the environment

```bash
astro dev restart
```

---

## 📘 Notes

* Default Airflow UI: [http://localhost:8080](http://localhost:8080)
* Variables can be set in the Web UI: **Admin → Variables**
* To use external providers, add to `requirements.txt`:

  ```
  apache-airflow-providers-postgres
  apache-airflow-providers-slack
  ```

---

## 🌐 Official User Guide

For detailed usage and configuration, refer to the official documentation:
👉 [Apache Airflow User Guide](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
👉 [Astro CLI docs](https://www.astronomer.io/docs/astro/cli/overview)

---

## 🧑‍🏫 Reference Instructor

This project is inspired by courses from:

* **Instructor:** [Marc Lamberti](https://www.udemy.com/user/lockgfg/)
* **Platform:** [Udemy](https://www.udemy.com/)
