"""
## Upgradeable
Improvable (for 3.8+) syntaxes

"""

__author__ = "Batuhan Taskaya"

import ast

from inspectortiger.inspector import Inspector
from inspectortiger.plugins.context import Contexts, get_context
from inspectortiger.utils import (
    constant_check,
    is_single_node,
    name_check,
    target_check,
)


@Inspector.register(ast.For)
def yield_from(node, db):
    """Yield can be replaced with yield from."""

    if (
        is_single_node(node, ast.Expr)
        and isinstance(node.body[0].value, ast.Yield)
        and target_check(node.body[0].value.value, node.target)
    ):
        return node.body[0].value


@Inspector.register(ast.Call)
def super_args(node, db):
    """`super()` called with arguments (old style)."""
    if (
        get_context(node, db) is db["upgradeable"]["context"]
        and db["upgradeable"]["context"].context is Contexts.FUNCTION
        and db["upgradeable"]["previous_contexts"][-1].context
        is Contexts.CLASS
        and name_check(node.func, "super")
        and node.args
    ):
        return node


@Inspector.register(ast.Subscript)
def optional(node, db):
    """`Union[Type, None]` can be replaced with `Optional[Type]`."""
    if (
        name_check(node.value, "Union")
        and isinstance(node.slice.value, ast.Tuple)
        and len(node.slice.value.elts) == 2
        and len(
            list(
                filter(
                    lambda node: constant_check(node, None),
                    node.slice.value.elts,
                )
            )
        )
    ):
        return node.value
