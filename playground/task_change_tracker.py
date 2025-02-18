import os
import json
import hashlib
import smtplib
import difflib
from datetime import datetime
from typing import Dict, List, Optional, Set
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import ast
from pathlib import Path


class AirflowTaskParser:
    """Parser to extract task definitions from Airflow DAG files"""

    def __init__(self):
        self.task_types = {
            "PythonOperator",
            "BashOperator",
            "SqlOperator",
            "EmailOperator",
            "SimpleHttpOperator",
            "DummyOperator",
            "SubDagOperator",
            # Add more operator types as needed
        }

    def extract_tasks_from_file(self, file_path: str) -> Dict[str, dict]:
        """
        Extract all task definitions from a DAG file
        Returns: Dict[task_id, task_info]
        """
        with open(file_path, "r") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            logging.error(f"Failed to parse {file_path}")
            return {}

        tasks = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                task_info = self._extract_task_from_assignment(node)
                if task_info:
                    tasks[task_info["task_id"]] = task_info

        return tasks

    def _extract_task_from_assignment(self, node: ast.Assign) -> Optional[dict]:
        """Extract task information from an assignment node"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                task_name = target.id
                if isinstance(node.value, ast.Call):
                    operator_type = self._get_operator_type(node.value)
                    if operator_type:
                        return {
                            "task_id": task_name,
                            "operator": operator_type,
                            "content": self._get_task_content(node),
                            "dependencies": self._get_task_dependencies(node),
                            "line_number": node.lineno,
                        }
        return None

    def _get_operator_type(self, node: ast.Call) -> Optional[str]:
        """Get the type of Airflow operator"""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.task_types:
                return node.func.id
        return None

    def _get_task_content(self, node: ast.Assign) -> str:
        """Get the full content of the task definition"""
        return ast.unparse(node)

    def _get_task_dependencies(self, node: ast.Assign) -> List[str]:
        """Extract task dependencies (if available in the same file)"""
        dependencies = []
        # This is a simplified version - in practice, you'd need to track
        # set_upstream/set_downstream calls and >> / << operators
        return dependencies


class TaskChangeTracker:
    """Track changes in Airflow tasks across all DAGs"""

    def __init__(self, dags_folder: str):
        self.dags_folder = dags_folder
        self.parser = AirflowTaskParser()
        self.db_file = "task_history.json"
        self.email_config = {
            "smtp_server": "smtp.company.com",
            "smtp_port": 587,
            "sender_email": "airflow-monitor@company.com",
            "recipients": ["airflow-team@company.com"],
        }

    def scan_all_dags(self):
        """Scan all DAG files and track changes"""
        current_state = {}
        changes = []

        # Scan all Python files in the DAGs folder
        for dag_file in Path(self.dags_folder).rglob("*.py"):
            if self._is_dag_file(dag_file):
                dag_tasks = self.parser.extract_tasks_from_file(str(dag_file))
                current_state[str(dag_file)] = dag_tasks

        # Compare with previous state
        previous_state = self._load_previous_state()
        changes = self._detect_changes(previous_state, current_state)

        if changes:
            self._send_notification(changes)
            self._save_state(current_state)

        return changes

    def _is_dag_file(self, file_path: Path) -> bool:
        """Check if a file is likely to be a DAG file"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
            return "airflow" in content.lower() and "dag" in content.lower()
        except:
            return False

    def _load_previous_state(self) -> Dict:
        """Load the previous state from the database"""
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_state(self, state: Dict):
        """Save the current state to the database"""
        with open(self.db_file, "w") as f:
            json.dump(state, f, indent=2)

    def _detect_changes(self, previous: Dict, current: Dict) -> List[dict]:
        """Detect changes between previous and current states"""
        changes = []

        # Check for changes in existing DAGs
        for dag_file in set(previous.keys()) | set(current.keys()):
            prev_tasks = previous.get(dag_file, {})
            curr_tasks = current.get(dag_file, {})

            # Check for added/modified/removed tasks
            for task_id in set(prev_tasks.keys()) | set(curr_tasks.keys()):
                if task_id not in prev_tasks:
                    changes.append(
                        {
                            "dag_file": dag_file,
                            "task_id": task_id,
                            "change_type": "added",
                            "details": curr_tasks[task_id],
                        }
                    )
                elif task_id not in curr_tasks:
                    changes.append(
                        {
                            "dag_file": dag_file,
                            "task_id": task_id,
                            "change_type": "removed",
                            "details": prev_tasks[task_id],
                        }
                    )
                elif prev_tasks[task_id] != curr_tasks[task_id]:
                    diff = "\n".join(
                        difflib.unified_diff(
                            prev_tasks[task_id]["content"].splitlines(),
                            curr_tasks[task_id]["content"].splitlines(),
                            fromfile=f"Previous {task_id}",
                            tofile=f"Current {task_id}",
                            lineterm="",
                        )
                    )
                    changes.append(
                        {
                            "dag_file": dag_file,
                            "task_id": task_id,
                            "change_type": "modified",
                            "diff": diff,
                            "details": curr_tasks[task_id],
                        }
                    )

        return changes

    def _send_notification(self, changes: List[dict]):
        """Send email notification about detected changes"""
        msg = MIMEMultipart()
        msg["From"] = self.email_config["sender_email"]
        msg["To"] = ", ".join(self.email_config["recipients"])
        msg["Subject"] = (
            f'Airflow Task Changes Detected - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        )

        body = "The following changes were detected in Airflow tasks:\n\n"

        for change in changes:
            body += f"DAG File: {change['dag_file']}\n"
            body += f"Task ID: {change['task_id']}\n"
            body += f"Change Type: {change['change_type']}\n"

            if "diff" in change:
                body += "Changes:\n"
                body += change["diff"]

            body += "\nTask Details:\n"
            body += json.dumps(change["details"], indent=2)
            body += "\n" + "=" * 50 + "\n\n"

        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(
                self.email_config["smtp_server"], self.email_config["smtp_port"]
            ) as server:
                server.starttls()
                server.send_message(msg)
                logging.info("Change notification email sent successfully")
        except Exception as e:
            logging.error(f"Failed to send email notification: {str(e)}")


def main():
    """Main function to run the task tracker"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="task_tracker.log",
    )

    dags_folder = os.environ.get("AIRFLOW_HOME", "/opt/airflow/dags")
    tracker = TaskChangeTracker(dags_folder)
    changes = tracker.scan_all_dags()

    if changes:
        logging.info(f"Detected {len(changes)} changes in tasks")
    else:
        logging.info("No changes detected")


if __name__ == "__main__":
    main()
