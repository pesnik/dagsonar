from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class DagConfig:
    path: Path
    tasks: List[str]


@dataclass
class ShellScriptReference:
    path: Path
    content: str


@dataclass
class ExprReference:
    name: str
    content: str


@dataclass
class TaskReference:
    task_id: Optional[str] = None
    task_type: Optional[str] = None
    content: Optional[str] = None
    shell_scripts: List[ShellScriptReference] = field(
        default_factory=list
    )  # [(path, content)]
    external_variables: List[ExprReference] = field(
        default_factory=list
    )  # [(name, content)]
    called_functions: List[ExprReference] = field(
        default_factory=list
    )  # [(name, content)]
    hash: Optional[str] = None
    last_modified: Optional[str] = None


@dataclass
class DagReference:
    dag_id: str
    task_history: List[TaskReference]
