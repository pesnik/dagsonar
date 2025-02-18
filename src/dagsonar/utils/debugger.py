import ast
from pprint import pprint


def debug(node: ast.AST):
    pprint(ast.dump(node))
