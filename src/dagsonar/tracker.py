import ast

from dagsonar.parser import Parser
from dagsonar.utils.debugger import debug
import hashlib


class TaskTracker:
    """Main class for tracking DAG task changes."""

    def __init__(self, dags_folder: str, notification_config: dict | None = None):
        self.dags_folder = dags_folder
        self.notification_config = notification_config or {}

    def start_monitoring(self):
        """Start monitoring DAG tasks for changes."""
        pass

    def scan_for_changes(self):
        """Perform a single scan for changes."""
        parser = Parser("/Users/r_hasan/Development/dagsonar/playground/dag_tester.py")
        tasks = parser.get_tasks(["task_start", "task_cmd", "task_sensor", "end"])
        tracker = []
        for task in tasks:
            if isinstance(task, ast.FunctionDef):
                # TODO: if task is a Bash Decorator, then track the shell file if referred
                tracker.append(task)
                def traverse(head, intend = 0):
                    # print("\t->" * intend + (ast.dump(head)))
                    if isinstance(head, ast.Name):
                        var = parser.find_variable_reference(variable=head)
                        if var.value is not None:
                            tracker.append(var)
                    if isinstance(head, ast.Call):
                        if isinstance(head.func, ast.Name):
                            fn = parser.find_function_reference(fn=head.func)
                            if fn is not None:
                                tracker.append(fn)
                    for child in ast.iter_child_nodes(head):
                        traverse(child, intend + 1)
                traverse(task)
            else:
                # TODO: if task is a BashOperator, then track the shell file if referred
                tracker.append(task)
                for arg in task.args:
                    pass
                for keyword in task.keywords:
                    if isinstance(keyword.value, ast.Name):
                        ref = parser.find_variable_reference(keyword.value)
                        keyword.value = ref
                        tracker.append(keyword)

        contents = ""
        for task in tracker:
            contents += ast.dump(task)
        hash = hashlib.sha256(contents.encode()).hexdigest()
        print(hash)

if __name__ == "__main__":
    tracker = TaskTracker(".")
    tracker.scan_for_changes()
