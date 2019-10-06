"""
## Misc
Common gotchas

"""

__author__ = "Batuhan Taskaya"

import ast

from inspectortiger.configmanager import Plugin
from inspectortiger.inspector import Inspector
from inspectortiger.plugins.context import get_context
from inspectortiger.plugins.parentize import parent_to

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
