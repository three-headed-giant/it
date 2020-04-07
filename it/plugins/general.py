"""
## General
Common gotchas

- `db['general']['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value
"""

__author__ = "Batuhan Taskaya"

import ast
import inspect

from it.inspector import Inspector
from it.plugin import Plugin
from it.plugins.context import get_context
from it.plugins.parentize import parent_to
from it.utils import name_check

MUTABLE_TYPE = (ast.List, ast.Dict, ast.Set)


@Inspector.register(ast.FunctionDef)
def default_mutable_arg(node, db):
    """Default argument is something mutable.

    ```py
    def foo(x = []): ...
    ```
    """

    if any(
        isinstance(default, MUTABLE_TYPE) for default in node.args.defaults
    ):
        return node.args


@Inspector.register(ast.Try)
@Plugin.require("@context")
def control_flow_inside_finally(node, db):
    """A return/break/continue that would implicitly cancel any active exception.

    ```py
    def foo():
        try:
            foo()
        finally:
            return
    ```
    """

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


def traverse_exception(base, exceptions=None):
    exceptions = exceptions or {}

    if base.__name__ not in exceptions:
        exceptions[base.__name__] = ()

    for exc in base.__subclasses__():
        exceptions[exc.__name__] = tuple(
            base.__name__
            for base in inspect.getmro(exc)
            if issubclass(base, BaseException)
        )
        traverse_exception(exc, exceptions)

    return exceptions.copy()


EXC_TREE = traverse_exception(BaseException)
ALL_EXCS = EXC_TREE.keys()


@Inspector.register(ast.ClassDef)
def exception_defs(node, db):
    exc_bases = tuple(
        EXC_TREE[base.id] for base in node.bases if name_check(base, *ALL_EXCS)
    )
    if exc_bases:
        EXC_TREE[node.name] = exc_bases
        db["general"]["user_exceptions"][node.name] = exc_bases


@Inspector.register(ast.Try)
def unreachable_except(node, db):
    """Except statement is unreachable due to a more broad except.

    ```py
    try:
        raise ValueError
    except Exception:
        pass
    except ValueError:
        pass
    ```
    """

    handlers = [
        handler.type.id
        for handler in node.handlers
        if isinstance(handler.type, ast.Name)
    ]

    seen = set()
    for handler in handlers:
        bases = EXC_TREE.get(handler)
        if bases is None:
            return False

        if any(base in seen for base in bases):
            return True
        else:
            seen.add(handler)
