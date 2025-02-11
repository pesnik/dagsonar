# DagSonar 🔍

Deep visibility into your Airflow task changes

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Apache Airflow](https://img.shields.io/badge/apache--airflow-2.0+-yellow.svg)](https://airflow.apache.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/dagsonar.svg)](https://badge.fury.io/py/dagsonar)

## What is DagSonar?

DagSonar is like having a high-precision radar system for your Airflow tasks. It detects, tracks, and notifies you about task changes across your entire Airflow environment, ensuring you never miss critical modifications to your DAGs.

![DagSonar Demo](docs/images/dagsonar-demo.gif)

## ✨ Key Features

- 🎯 **Precise Detection**: Catches even the smallest task changes using AST parsing
- 🔄 **Real-time Monitoring**: Continuous tracking of all DAG modifications
- 📊 **Rich Diffs**: Visual and detailed change comparisons
- 📧 **Smart Notifications**: Configurable alerts for task modifications
- 🏗️ **Multi-Operator Support**: Works with all standard Airflow operators
- 📈 **Change History**: Maintains a searchable audit trail
- 🛡️ **Production Ready**: Built for reliability and performance

## 🚀 Quick Start

### Installation

```bash
pip install dagsonar
```

### Basic Usage

```python
from dagsonar import TaskTracker

# Initialize the tracker
tracker = TaskTracker(
    dags_folder='/path/to/dags',
    notification_config={
        "smtp_server": "smtp.company.com",
        "smtp_port": 587,
        "sender": "dagsonar@company.com",
        "recipients": ["team@company.com"]
    }
)

# Start monitoring
tracker.start_monitoring()
```

### As an Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

dag = DAG(
    'dagsonar_monitor',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 2, 11),
    catchup=False,
    tags=['monitoring']
)

def run_dagsonar():
    from dagsonar import TaskTracker
    tracker = TaskTracker('/opt/airflow/dags')
    tracker.scan_for_changes()

monitor_tasks = PythonOperator(
    task_id='scan_task_changes',
    python_callable=run_dagsonar,
    dag=dag
)
```

## 🎛️ Configuration

### Basic Configuration
```python
config = {
    "notification": {
        "smtp_server": "smtp.company.com",
        "smtp_port": 587,
        "sender": "dagsonar@company.com",
        "recipients": ["team@company.com"]
    },
    "monitoring": {
        "scan_interval": 3600,  # seconds
        "ignore_patterns": ["_tmp_", "test_"],
        "track_dependencies": True
    }
}
```

### Supported Operators
- PythonOperator
- BashOperator
- SqlOperator
- EmailOperator
- SimpleHttpOperator
- DummyOperator
- SubDagOperator
- Custom operators (configurable)

## 📊 Example Output

```diff
DAG: marketing_pipeline
Task: process_customer_data
--- Previous Version
+++ Current Version
@@ -1,5 +1,5 @@
 PythonOperator(
     task_id='process_customer_data',
-    python_callable=process_data,
+    python_callable=process_data_v2,
     dag=dag
 )
```

## 🤝 Contributing

We love contributions! Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/pesnin/dagsonar.git
cd dagsonar
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

## 📖 Documentation

Full documentation is available at [dagsonar.readthedocs.io](https://dagsonar.readthedocs.io)

## 🎯 Use Cases

- Monitor production DAGs for unexpected changes
- Track task modifications across multiple environments
- Maintain compliance with change management procedures
- Automate task change notifications
- Debug task configuration issues

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 💖 Acknowledgments

- Apache Airflow community
- All our contributors
- Users who provide valuable feedback

---
Made with 🚀 for the Airflow community
