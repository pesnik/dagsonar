import json
from dataclasses import asdict
from pathlib import Path

from dagsonar.models import (DagReference, ExprReference, ShellScriptReference,
                             TaskReference)


class ReferenceEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(
            o, (DagReference, TaskReference, ShellScriptReference, ExprReference)
        ):
            return asdict(o)

        if isinstance(o, Path):
            return str(o)

        return super().default(o)
