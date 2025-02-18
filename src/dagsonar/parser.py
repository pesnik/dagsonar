import ast
from pprint import pprint
from typing import List


def debug(node: ast.AST):
    pprint(ast.dump(node))


class Parser:
    def __init__(self, file_loc):
        self.file_loc = file_loc
        with open(file_loc, "r") as f:
            self.tree = ast.parse(f.read())
            # debug(self.tree)

    def get_tasks(self, task_ids) -> List[ast.FunctionDef | ast.Call]:
        tasks = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and isinstance(node.value, ast.Call)
                        and target.id in task_ids
                    ):
                        if isinstance(node.value.func, ast.Name):
                            task = self.check_taskflow_operator(node.value.func.id)
                            print(node.value.func.id)
                            if task is not None:
                                tasks.append(task)
                            else:
                                tasks.append(node.value)
            elif isinstance(node, ast.FunctionDef) and node.name in task_ids:
                tasks.append(node)

        return tasks

    def check_taskflow_operator(self, id: str):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == id:
                return node
        return None


if __name__ == "__main__":
    parser = Parser("/Users/r_hasan/Development/dagsonar/playground/dag_tester.py")
    tasks = parser.get_tasks(["task_start", "task_cmd", "task_sensor", "end"])
    for task in tasks:
        debug(task)
