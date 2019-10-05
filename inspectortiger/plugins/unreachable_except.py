"""
## Unreachable Except
Unreacable excepts

- `db['unreachable_except']['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value
"""

__author__ = "Batuhan Taskaya"

import ast

from inspectortiger.inspector import Inspector
from inspectortiger.utils import name_check


def traverse_exception(base, exceptions=None, level=0):
    exceptions = exceptions or {}
    exceptions[base.__name__] = level
    level += 1
    for exc in base.__subclasses__():
        exceptions[exc.__name__] = level
        traverse_exception(exc, exceptions, level)
    return exceptions


EXC_TREE = traverse_exception(BaseException)
ALL_EXCS = EXC_TREE.keys()


@Inspector.register(ast.ClassDef)
def exception_defs(node, db):
    exc_bases = [base.id for base in node.bases if name_check(base, *ALL_EXCS)]
    if exc_bases:
        severity = min(EXC_TREE[exc] for exc in exc_bases)
        db["unreachable_except"]["user_exceptions"][node.name] = severity


@Inspector.register(ast.Try)
def unreachable_except(node, db):
    """Except statement is unreachable due to a more broad except."""

    handlers = [
        handler.type.id
        for handler in node.handlers
        if isinstance(handler.type, ast.Name)
    ]
    current_level = float("inf")
    for handler in handlers:
        level = EXC_TREE.get(handler)
        level = level or db["unreachable_except"]["user_exceptions"].get(
            handler
        )
        if level is None:
            return False
        if level > current_level:
            return True
        current_level = level
