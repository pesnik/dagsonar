from pathlib import Path

from dagsonar import DagConfig, TaskTracker


def test_task_tracker():
    tracker = TaskTracker()
    
    config = {
        "tester": DagConfig(
            path=Path("./playground/dag_tester.py"),
            tasks=["task_bash_op"],
        )
    }
    
    changes = tracker.track_changes(config, auto_save=False)
    print(changes)