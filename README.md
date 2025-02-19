# DagSonar

Deep visibility into your Airflow task changes through AST parsing and tracking

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Apache Airflow](https://img.shields.io/badge/apache--airflow-2.0+-yellow.svg)](https://airflow.apache.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

## What is DagSonar?

DagSonar is a monitoring tool that provides deep visibility into your Airflow DAG tasks by tracking changes through AST (Abstract Syntax Tree) parsing. It detects modifications in task definitions, external variables, shell scripts, and function calls, ensuring you never miss critical changes to your DAGs.

## Key Features

- **AST-Based Detection**: Tracks changes by parsing the Abstract Syntax Tree of your DAG files
- **Task Reference Tracking**: Monitors task definitions, external variables, and function calls
- **Shell Script Integration**: Tracks associated shell scripts referenced in BashOperator tasks
- **Change History**: Maintains a JSON-based history of all task modifications
- **Task Hash Generation**: Generates unique hashes for each task state to detect changes
- **Support for Multiple DAGs**: Track tasks across multiple DAG configurations

## Installation

```bash
pip install dagsonar
```

## Basic Usage

```python
from pathlib import Path
from dagsonar import TaskTracker, DagConfig

# Initialize the tracker
tracker = TaskTracker(history_file=Path("task_history.json"))

# Configure DAGs to track
dag_configs = {
    "example_dag": DagConfig(
        path=Path("/path/to/dag.py"),
        tasks=["task1", "task2"]  # Optional: specify tasks to track
    )
}

# Track tasks and get references
references = tracker.track_tasks(dag_configs)

# Check for changes
changes = tracker.check_for_changes(references)

# Save the new state
tracker.save_history(references)
```

## Features in Detail

### Task Reference Tracking

DagSonar tracks several aspects of your tasks:
- Task content and structure through AST
- External variable references
- Called functions
- Shell scripts referenced in bash tasks
- Task-specific hashes for change detection

### Supported Task Types

Currently supports tracking of:
- Function-based task definitions
- BashOperator task instances
- Referenced shell scripts
- External variable dependencies

## Configuration

### DagConfig
```python
from dagsonar import DagConfig
from pathlib import Path

config = DagConfig(
    path=Path("/path/to/dag.py"),  # Path to DAG file
    tasks=["task1", "task2"]       # Optional: List of specific tasks to track
)
```

### Task History

Task history is stored in JSON format with the following structure:
```json
[
  {
    "dag_id": "example_dag",
    "reference": {
      "dag_id": "example_dag",
      "task_history": [
        {
          "task_id": "task1",
          "content": "<ast_content>",
          "hash": "<computed_hash>",
          "external_variables": [],
          "called_functions": [],
          "shell_scripts": []
        }
      ]
    }
  }
]
```

## Contributing

We welcome contributions! Please check out our [Contributing Guide](CONTRIBUTING.md) to get started.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/pesnik/dagsonar.git
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

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Apache Airflow community
- All contributors and users providing valuable feedback

---
Built for the Airflow community
