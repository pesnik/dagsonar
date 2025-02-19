from pathlib import Path

from dagsonar import DagConfig, TaskTracker


def test_task_tracker():
    tracker = TaskTracker()

    config = {
        "tester": DagConfig(
            path=Path("/Users/r_hasan/Development/dagsonar/playground/dag_tester.py"),
            tasks=["end", "start", "cmd_task_sh", "task_bash_op"],
        )
    }
    new_reference = tracker.track_tasks(config)
    change_detected = tracker.check_for_changes(new_reference)
    tracker.save_history(new_reference)
    print(change_detected)
