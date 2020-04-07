"""
## Upgrade
Improvable (for 3.7+) syntaxes

"""

__author__ = "Batuhan Taskaya"

import ast
import string

from it.inspector import Inspector
from it.plugin import Plugin
from it.plugins.context import Contexts, get_context
from it.utils import (
    PY39_PLUS,
    biname_check,
    constant_check,
    get_slice,
    is_single_node,
    name_check,
    target_check,
    version_bound_check,
)


@Inspector.register(ast.For)
def yield_from(node, db):
    """`yield` can be replaced with `yield from`."""

    if (
        is_single_node(node, ast.Expr)
        and isinstance(node.body[0].value, ast.Yield)
        and target_check(node.body[0].value.value, node.target)
    ):
        return node.body[0].value


@Inspector.register(ast.Subscript)
def optional(node, db):
    """`Union[Type, None]` can be replaced with `Optional[Type]`."""

    if (
        name_check(node.value, "Union")
        and isinstance(get_slice(node), ast.Tuple)
        and len(get_slice(node).elts) == 2
        and len(
            list(
                filter(
                    lambda node: constant_check(node, None),
                    get_slice(node).elts,
                )
            )
        )
    ):
        return node.value


@Inspector.register(ast.Call)
@Plugin.require("@context")
def super_args(node, db):
    """`super(MyClass, self)` can be replaced with `super()`"""

    return (
        get_context(node, db) is db["context"]["context"]
        and db["context"]["context"].context is Contexts.FUNCTION
        and db["context"]["previous_contexts"][-1].context is Contexts.CLASS
        and name_check(node.func, "super")
        and node.args
    )


@Inspector.register(ast.For)
def builtin_enumerate(node, db):
    """`range(len(iterable))` can be replaced with `enumerate(iterable)`"""

    if (
        isinstance(node.iter, ast.Call)
        and name_check(node.iter.func, "range")
        and len(node.iter.args) == 1
        and isinstance(node.iter.args[0], ast.Call)
        and name_check(node.iter.args[0].func, "len")
        and len(node.iter.args[0].args) == 1
    ):
        target = node.target
        iterable = node.iter.args[0].args[0]
        for subnode in ast.walk(node):
            if (
                isinstance(subnode, ast.Subscript)
                and isinstance(subnode.ctx, ast.Load)
                and version_bound_check(subnode.slice, "Index", PY39_PLUS)
                and biname_check(subnode.value, iterable)
                and biname_check(get_slice(subnode), target)
            ):
                return node.iter


@Inspector.register(ast.Call)
def use_comprehension(node, db):
    """`list`/`dict`/`set` calls with a generator expression
    can be replaced with comprehensions."""

    if (
        name_check(node.func, "list", "set", "dict")
        and len(node.args) == 1
        and len(node.keywords) == 0
        and isinstance(node.args[0], ast.GeneratorExp)
    ):
        if not name_check(node.func, "dict"):
            return True
        return (
            isinstance(node.args[0].elt, ast.Tuple)
            and len(node.args[0].elt.elts) == 2
        )


@Inspector.register(ast.Call)
def map_use_comprehension(node, db):
    """A map (to a complex callable) can be replaced with 
    `list` or `set` comprehensions."""

    return (
        name_check(node.func, "list", "set")
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Call)
        and name_check(node.args[0].func, "map")
        and len(node.args[0].args) == 2
        and not isinstance(node.args[0].args[0], (ast.Name, ast.Attribute))
    )


@Inspector.register(ast.Assign)
def alphabet_constant(node, db):
    """A constant literal with the value of ASCII alphabet (`x = "ABC....Z"`) can be replaced 
    with `string.ascii_letters`/`string.ascii_uppercase`/`string.ascii_lowercase`
    
    ```py
    GUESS_MY_NAME = "abcde...WXYZ"
    UPPERCASE_ALPH = "ABCD...WXYZ"
    LOWERCASE_ALPH = "abcd...wxyz"
    
    def game(char):
        return char in GUESS_MY_NAME
    ```
    to
    ```py
    import string
    UPPERCASE_ALPH = string.ascii_uppercase
    LOWERCASE_ALPH = string.ascii_lowercase
    
    def game(char):
        return char in string.ascii_letters
    ```
    """

    return (
        len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id.isupper()
        and constant_check(
            node.value,
            string.ascii_letters,
            string.ascii_uppercase,
            string.ascii_lowercase,
        )
    )


@Inspector.register(ast.Try)
def suppress(node, db):
    """A try statement with one except which only passes can be 
    replaced with `contextlib.suppress`"""

    return len(node.handlers) == 1 and is_single_node(
        node.handlers[0], ast.Pass
    )
