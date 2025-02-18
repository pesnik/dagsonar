import os
import json
import smtplib
import difflib
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Set
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="dag_changes.log",
)


class DAGChangeNotifier:
    def __init__(self):
        """Initialize the DAG change notifier with inline configuration"""
        # Inline configuration instead of loading from file
        self.config = {
            "monitored_tasks": {
                # "task_tpt_exp_bad_debt_loan": ["task_bad_debt_loan_rpt_push"],
                # "task_tpt_exp_bad_debt_data": ["task_bad_debt_data_rpt_push"],
                # "task_tpt_exp_subs_base": ["task_vas_subs_base_push"],
                "cmd_bad_debt_data_rpt_push": ["cmd_bad_debt_data_rpt_push"],
            },
            "email_config": {
                "smtp_server": "smtp.banglalink.net",
                "smtp_port": 587,
                "sender_email": "mr.hasan@banglalink.net",
                "recipients": ["mr.hasan@banglalink.net"],
            },
        }
        self.cache_file = "dag_task_cache.json"
        self.monitored_tasks = self.config["monitored_tasks"]
        self.email_config = self.config["email_config"]

    def _get_task_hash(self, task_content: str) -> str:
        """Generate hash for task content"""
        return hashlib.sha256(task_content.encode()).hexdigest()

    def _load_task_cache(self) -> Dict[str, str]:
        """Load cached task hashes"""
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_task_cache(self, cache: Dict[str, str]):
        """Save task hashes to cache"""
        with open(self.cache_file, "w") as f:
            json.dump(cache, f, indent=4)

    def _extract_task_content(self, dag_file_path: str, task_id: str) -> str:
        """Extract task content from DAG file"""
        try:
            with open(dag_file_path, "r") as f:
                content = f.read()
                # Basic task content extraction - this could be enhanced with better parsing
                task_start = content.find(f"{task_id} = ")
                if task_start == -1:
                    return ""

                # Find the end of the task definition
                task_end = content.find("\n\n", task_start)
                if task_end == -1:
                    task_end = len(content)

                return content[task_start:task_end]
        except FileNotFoundError:
            logging.error(f"DAG file not found at {dag_file_path}")
            return ""

    def _send_email_notification(self, changes: List[dict]):
        """Send email notification about task changes"""
        msg = MIMEMultipart()
        msg["From"] = self.email_config["sender_email"]
        msg["To"] = ", ".join(self.email_config["recipients"])
        msg["Subject"] = "DAG Task Changes Detected"

        body = "The following changes were detected in monitored DAG tasks:\n\n"
        for change in changes:
            body += f"Task: {change['task_id']}\n"
            body += f"Type of Change: {change['change_type']}\n"
            if "diff" in change:
                body += "Changes:\n"
                body += change["diff"]
            body += "\nDownstream Tasks Affected:\n"
            body += ", ".join(change["downstream_tasks"])
            body += "\n\n" + "=" * 50 + "\n\n"

        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(
                self.email_config["smtp_server"], self.email_config["smtp_port"]
            ) as server:
                server.starttls()
                server.send_message(msg)
                logging.info("Notification email sent successfully")
        except Exception as e:
            logging.error(f"Failed to send email notification: {str(e)}")

    def check_for_changes(self, dag_file_path: str):
        """
        Check for changes in monitored tasks and notify if changes are detected

        Args:
            dag_file_path: Path to the DAG file
        """
        cache = self._load_task_cache()
        changes = []

        for task_id in self.monitored_tasks.keys():
            current_content = self._extract_task_content(dag_file_path, task_id)
            current_hash = self._get_task_hash(current_content)

            if task_id not in cache:
                # New task
                changes.append(
                    {
                        "task_id": task_id,
                        "change_type": "New Task Added",
                        "downstream_tasks": self.monitored_tasks[task_id],
                    }
                )
            elif cache[task_id] != current_hash:
                # Changed task
                old_content = cache[task_id]
                diff = "\n".join(
                    difflib.unified_diff(
                        old_content.splitlines(),
                        current_content.splitlines(),
                        fromfile="Previous Version",
                        tofile="Current Version",
                        lineterm="",
                    )
                )

                changes.append(
                    {
                        "task_id": task_id,
                        "change_type": "Task Modified",
                        "diff": diff,
                        "downstream_tasks": self.monitored_tasks[task_id],
                    }
                )

            cache[task_id] = current_hash

        if changes:
            self._send_email_notification(changes)
            self._save_task_cache(cache)
            logging.info(f"Detected {len(changes)} changes in monitored tasks")
        else:
            logging.info("No changes detected in monitored tasks")


def main():
    """Main function to run the DAG change notifier"""
    notifier = DAGChangeNotifier()
    dag_file_path = os.environ.get(
        "DAG_FILE_PATH", "finance_month_closing_automation.py"
    )
    notifier.check_for_changes(dag_file_path)


if __name__ == "__main__":
    main()
