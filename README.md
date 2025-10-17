# 🚀 Airflow-Training

[![Docker](https://img.shields.io/badge/run%20with-Docker-blue?logo=docker)](https://www.docker.com/get-started/) [![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.x-orange?logo=apacheairflow)](https://airflow.apache.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

---

## 🌍 Overview

This repository provides a complete and ready-to-run **Apache Airflow learning environment**.

Key features:

* Ready-to-run Airflow setup via Docker or Astronomer CLI.
* Practical DAG examples for ETL, scheduling, and data orchestration.
* Slack integration and Postgres connection examples.

---

## 📦 Project Structure

```
AIRFLOW-TRAINING/
├── dags/                # All DAGs (organized by category)
├── include/             # Shared Python modules (utils)
├── img/                 # Images used in documentation
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

### Initialize the project

```bash
astro dev init
```

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

## 🌐 Official User Guide

For detailed usage and configuration, refer to the official documentation:
👉 [Apache Airflow User Guide](https://airflow.apache.org/docs/apache-airflow/stable/index.html)

---

## 🧠 Learning Focus

This repository helps you understand:

* DAG scheduling and dependencies
* Task retries, sensors, and custom operators
* XCom and parameter passing
* Slack and Postgres integration
* Managing environment variables in Airflow UI

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

## 🧑‍🏫 Reference Instructor

This project is inspired by courses from:

* **Instructor:** [Marc Lamberti](https://www.udemy.com/user/lockgfg/)
* **Platform:** [Udemy](https://www.udemy.com/)
