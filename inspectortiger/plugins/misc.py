""" General checks about code quality and common mistakes """

__author__ = "Batuhan Taskaya"

import ast

from inspectortiger.inspector import Inspector
from inspectortiger.utils import Level

MUTABLE_TYPE = (ast.List, ast.Dict, ast.Set)


@Inspector.register(ast.FunctionDef)
@Level.HIGH
def default_mutable_arg(node, db):
    return any(isinstance(default, MUTABLE_TYPE) for default in node.args.defaults)
