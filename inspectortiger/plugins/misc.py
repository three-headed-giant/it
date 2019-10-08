"""
## Misc
Common gotchas

- `db['unreachable_except']['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value
"""

__author__ = "Batuhan Taskaya"

import ast

from inspectortiger.config_manager import Plugin
from inspectortiger.inspector import Inspector
from inspectortiger.plugins.context import get_context
from inspectortiger.plugins.parentize import parent_to
from inspectortiger.utils import name_check

MUTABLE_TYPE = (ast.List, ast.Dict, ast.Set)


@Inspector.register(ast.FunctionDef)
def default_mutable_arg(node, db):
    """Default argument is something mutable."""

    if any(
        isinstance(default, MUTABLE_TYPE) for default in node.args.defaults
    ):
        return node.args


@Inspector.register(ast.Try)
@Plugin.require("@context")
def control_flow_inside_finally(node, db):
    """A return/break/continue that would implicitly cancel any active exception."""

    for subnode in node.finalbody:
        for child in ast.walk(subnode):
            if isinstance(child, ast.Return) and get_context(
                child, db
            ) is get_context(node, db):
                return child
            elif isinstance(child, (ast.Break, ast.Continue)) and not any(
                isinstance(parent, ast.For)
                for parent in parent_to(child, node)
            ):
                return child
            else:
                continue


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
