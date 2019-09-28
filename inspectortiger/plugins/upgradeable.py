"""
## Upgradeable
Finds syntaxes that can be improvable (for 3.8+)

- Checks if a yield can be replaced with yield from
- Checks if `super()` called with arguments (old style)
"""

__author__ = "Batuhan Taskaya"

import ast

from inspectortiger.inspector import Inspector
from inspectortiger.plugins.context import Contexts, get_context
from inspectortiger.utils import is_single_node, name_check, target_check


@Inspector.register(ast.For)
def yield_from(node, db):
    return (
        is_single_node(node, ast.Expr)
        and isinstance(node.body[0].value, ast.Yield)
        and target_check(node.body[0].value.value, node.target)
    )


@Inspector.register(ast.Call)
def super_args(node, db):
    return (
        get_context(node, db) is db["context"]
        and db["context"].context is Contexts.FUNCTION
        and db["previous_contexts"][-1].context is Contexts.CLASS
        and name_check(node.func, "super")
        and node.args
    )
