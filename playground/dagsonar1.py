from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
import ast
import hashlib
import json
import difflib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeType(Enum):
    TASK_ADDED = "task_added"
    TASK_REMOVED = "task_removed"
    OPERATOR_CHANGED = "operator_changed"
    ARGS_CHANGED = "args_changed"
    KWARGS_CHANGED = "kwargs_changed"
    DEPENDENCIES_CHANGED = "dependencies_changed"
    SCHEDULE_CHANGED = "schedule_changed"

@dataclass
class TaskDefinition:
    """Represents a task's complete definition at a point in time."""
    name: str
    operator: str
    args: tuple
    kwargs: dict
    dependencies: Set[str]
    schedule: Optional[str]
    
    def get_hash(self) -> str:
        """Generate a hash of the task's definition for quick comparison."""
        task_dict = {
            "name": self.name,
            "operator": self.operator,
            "args": self.args,
            "kwargs": self.kwargs,
            "dependencies": sorted(list(self.dependencies)),
            "schedule": self.schedule
        }
        return hashlib.sha256(
            json.dumps(task_dict, sort_keys=True).encode()
        ).hexdigest()

@dataclass
class TaskChange:
    """Represents a detected change in a task."""
    timestamp: datetime
    dag_id: str
    task_name: str
    change_type: ChangeType
    old_value: Any
    new_value: Any
    
    def get_diff(self) -> str:
        """Generate a human-readable diff of the change."""
        if isinstance(self.old_value, dict) and isinstance(self.new_value, dict):
            return self._dict_diff(self.old_value, self.new_value)
        return f"Changed from {self.old_value} to {self.new_value}"
    
    def _dict_diff(self, old_dict: dict, new_dict: dict) -> str:
        """Generate a readable diff of two dictionaries."""
        old_str = json.dumps(old_dict, indent=2, sort_keys=True)
        new_str = json.dumps(new_dict, indent=2, sort_keys=True)
        diff = difflib.unified_diff(
            old_str.splitlines(),
            new_str.splitlines(),
            lineterm=''
        )
        return '\n'.join(diff)

class DagParser:
    """Parses DAG files to extract task definitions."""
    
    def parse_dag_file(self, dag_path: Path) -> Dict[str, TaskDefinition]:
        """Parse a DAG file and return a dictionary of task definitions."""
        with open('finance_month_closing_automation.py', 'r') as f:
            tree = ast.parse(f.read())
            
        tasks = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                task_def = self._extract_task_definition(node)
                if task_def:
                    tasks[task_def.name] = task_def
                    
        return tasks
    
    def _extract_task_definition(self, node: ast.Assign) -> Optional[TaskDefinition]:
        """Extract task definition from an assignment node."""
        # This is a simplified example - real implementation would need to handle
        # more complex cases and different operator patterns
        if isinstance(node.value, ast.Call):
            operator = self._get_operator_name(node.value)
            if operator:
                return TaskDefinition(
                    name=node.targets[0].id if hasattr(node.targets[0], 'id') else None,
                    operator=operator,
                    args=self._extract_args(node.value.args),
                    kwargs=self._extract_kwargs(node.value.keywords),
                    dependencies=self._extract_dependencies(node),
                    schedule=None  # Would be extracted from DAG definition
                )
        return None

class ChangeDetector(FileSystemEventHandler):
    """Detects and tracks changes in DAG files."""
    
    def __init__(self, tracked_dags: Set[Path], task_filters: Dict[Path, Set[str]]):
        self.tracked_dags = tracked_dags
        self.task_filters = task_filters
        self.parser = DagParser()
        self.task_states: Dict[Path, Dict[str, TaskDefinition]] = {}
        self.changes: List[TaskChange] = []
        
        # Initialize current state
        self._initialize_states()
    
    def _initialize_states(self):
        """Initialize the current state of all tracked DAGs and tasks."""
        for dag_path in self.tracked_dags | self.task_filters.keys():
            self.task_states[dag_path] = self.parser.parse_dag_file(dag_path)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            path = Path(event.src_path).resolve()
            if path in self.tracked_dags or path in self.task_filters:
                self._check_for_changes(path)
    
    def _check_for_changes(self, dag_path: Path):
        """Check for changes in a DAG file."""
        old_state = self.task_states[dag_path]
        new_state = self.parser.parse_dag_file(dag_path)
        
        # Get relevant task names based on tracking configuration
        tracked_tasks = (self.task_filters.get(dag_path) 
                        if dag_path in self.task_filters 
                        else set(new_state.keys()))
        
        # Check for added tasks
        for task_name in set(new_state.keys()) - set(old_state.keys()):
            if task_name in tracked_tasks:
                self._record_change(
                    dag_path,
                    task_name,
                    ChangeType.TASK_ADDED,
                    None,
                    new_state[task_name]
                )
        
        # Check for removed tasks
        for task_name in set(old_state.keys()) - set(new_state.keys()):
            if task_name in tracked_tasks:
                self._record_change(
                    dag_path,
                    task_name,
                    ChangeType.TASK_REMOVED,
                    old_state[task_name],
                    None
                )
        
        # Check for modifications in existing tasks
        for task_name in set(old_state.keys()) & set(new_state.keys()):
            if task_name in tracked_tasks:
                self._check_task_changes(
                    dag_path,
                    task_name,
                    old_state[task_name],
                    new_state[task_name]
                )
        
        # Update state
        self.task_states[dag_path] = new_state
    
    def _check_task_changes(
        self,
        dag_path: Path,
        task_name: str,
        old_task: TaskDefinition,
        new_task: TaskDefinition
    ):
        """Check for changes between old and new task definitions."""
        if old_task.operator != new_task.operator:
            self._record_change(
                dag_path,
                task_name,
                ChangeType.OPERATOR_CHANGED,
                old_task.operator,
                new_task.operator
            )
            
        if old_task.args != new_task.args:
            self._record_change(
                dag_path,
                task_name,
                ChangeType.ARGS_CHANGED,
                old_task.args,
                new_task.args
            )
            
        if old_task.kwargs != new_task.kwargs:
            self._record_change(
                dag_path,
                task_name,
                ChangeType.KWARGS_CHANGED,
                old_task.kwargs,
                new_task.kwargs
            )
            
        if old_task.dependencies != new_task.dependencies:
            self._record_change(
                dag_path,
                task_name,
                ChangeType.DEPENDENCIES_CHANGED,
                old_task.dependencies,
                new_task.dependencies
            )
            
        if old_task.schedule != new_task.schedule:
            self._record_change(
                dag_path,
                task_name,
                ChangeType.SCHEDULE_CHANGED,
                old_task.schedule,
                new_task.schedule
            )
    
    def _record_change(
        self,
        dag_path: Path,
        task_name: str,
        change_type: ChangeType,
        old_value: Any,
        new_value: Any
    ):
        """Record a detected change."""
        change = TaskChange(
            timestamp=datetime.now(),
            dag_id=dag_path.stem,
            task_name=task_name,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value
        )
        self.changes.append(change)
        
        
# Example usage in TaskTracker
def start_tracking(self):
    detector = ChangeDetector(self._tracked_dags, self._task_filters)
    observer = Observer()
    
    for dag_path in self._tracked_dags | self._task_filters.keys():
        observer.schedule(detector, str(dag_path.parent), recursive=False)
    
    observer.start()