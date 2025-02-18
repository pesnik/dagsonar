import ast
from pprint import pprint
from typing import Dict


def parse_dag_file(dag_path):
    """Parse a DAG file and return a dictionary of task definitions."""
    with open(dag_path, "r") as f:
        tree = ast.parse(f.read())

        pprint(ast.dump(tree))


parse_dag_file("dag_tester.py")
