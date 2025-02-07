# ----------------------------------------------------------------------
# Python expression utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import ast
from typing import List, Set, Any, Callable

# NOC modules
from noc.core.convert.dbm import dbm2mw, mw2dbm

FN_LOCALS = {"dbm2mw": dbm2mw, "mw2dbm": mw2dbm}


class _VarVisitor(ast.NodeVisitor):
    """
    Collect all variable names from expression
    """

    def __init__(self):
        super().__init__()
        self.vars: Set[str] = set()
        self.skip: Set[str] = set()

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id not in self.skip:
            self.vars.add(node.id)

    def visit_Call(self, node: ast.Call) -> Any:
        self.skip.add(node.func.id)
        self.generic_visit(node)

    def get_vars(self) -> List[str]:
        return list(sorted(self.vars))


def get_vars(expr: str) -> List[str]:
    """
    Parse expression and get the list of variables
    :param expr:
    :return:
    """
    tree = ast.parse(expr, mode="eval")
    visitor = _VarVisitor()
    visitor.visit(tree)
    return visitor.get_vars()


def get_fn(expr: str) -> Callable:
    """
    Compile expression to function
    :param expr:
    :return:
    """
    x_vars = get_vars(expr)
    src = f"def fn({','.join(x_vars)}):\n    return {expr}\n"
    ctx = {}
    exec(src, FN_LOCALS, ctx)
    return ctx["fn"]
