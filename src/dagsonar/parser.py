import ast
from typing import List


class Parser:
    def __init__(self, file_loc):
        self.file_loc = file_loc
        with open(file_loc, "r") as f:
            self.tree = ast.parse(f.read())
            # debug(self.tree)

    def get_tasks(self, task_ids: List[str]) -> List[ast.FunctionDef | ast.Call]:
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
                            if task is not None:
                                tasks.append(task)
                            else:
                                tasks.append(node.value)
            elif isinstance(node, ast.FunctionDef) and node.name in task_ids:
                tasks.append(node)

        return tasks

    def check_taskflow_operator(self, id: str):
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.decorator_list is not None
                and node.name == id
            ):
                return node
        return None

    def find_variable_reference(self, variable: ast.Name) -> ast.Constant:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == variable.id:
                        if isinstance(node.value, ast.Constant):
                            return node.value

        return ast.Constant(value=None)

    def find_function_reference(self, fn: ast.Name) -> ast.FunctionDef | None:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == fn.id:
                    return node
        return None
