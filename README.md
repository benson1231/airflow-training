# airflow-training

[![Docker](https://img.shields.io/badge/run%20with-Docker-blue?logo=docker)](https://www.docker.com/get-started/) [![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.x-orange?logo=apacheairflow)](https://airflow.apache.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

---

## 🚀 Overview

This repository provides a minimal yet complete **Airflow learning environment**. It contains:

* Ready-to-run Docker Compose configuration.
* Practical DAG examples for ETL, scheduling, and data orchestration.

---

## 🧩 Requirements

You need **Docker** installed:
👉 [Get Docker](https://www.docker.com/get-started/)

Ensure Docker daemon is running before you start.

---

## 🧱 Quick Start

```bash
docker compose up
```

Then open your browser and navigate to:

```
http://localhost:8080
```

Default credentials (Airflow official default):

```
user: airflow
password: airflow
```

---

## 📂 Project Structure

```
airflow-training/
├── dags/                # Example DAGs for learning
├── docker-compose.yaml  # Airflow multi-service setup
├── logs/                # Runtime logs (auto-generated)
├── plugins/             # Custom operators or sensors
└── README.md
```

---

## 🧠 Learning Focus

* Task scheduling & dependencies
* XCom and parameter passing
* Sensors and custom operators
* Integrating Airflow with databases or APIs

---

## 📜 License

Released under the [MIT License](./LICENSE).
