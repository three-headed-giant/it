import ast
import builtins

from inspectortiger.inspector import Inspector
from inspectortiger.utils import (ALL_EXCS, EXC_TREE, MUTABLE_TYPE, Level,
                                  is_single_node, name_check, target_check)

if __debug__:
    from astpretty import pprint


@Inspector.register(ast.ClassDef)
@Level.WATCHER
def exception_defs(node, db):
    exc_bases = [base.id for base in node.bases if name_check(base, *ALL_EXCS)]
    if exc_bases:
        severity = min(EXC_TREE[exc] for exc in exc_bases)
        db["user_exceptions"][node.name] = severity


@Inspector.register(ast.Try)
@Level.HIGH
def unreachable_except(node, db):
    handlers = [
        handler.type.id
        for handler in node.handlers
        if isinstance(handler.type, ast.Name)
    ]
    current_level = float("inf")
    for handler in handlers:
        level = EXC_TREE.get(handler)
        level = level or db["user_exceptions"].get(handler)
        if level is None:
            return False
        if level > current_level:
            return True
        current_level = level


@Inspector.register(ast.Name)
@Level.AVG
def builtin_name_assignment(node, db):
    return isinstance(node.ctx, ast.Store) and name_check(node, *dir(builtins))


@Inspector.register(ast.Attribute)
@Level.EXTREME_LOW
def protected_access(node, db):
    return (
        node.attr.startswith("_")
        and not name_check(node.value, "self", "cls")
        and not node.attr.startswith("__")
    )


@Inspector.register(ast.For)
@Level.AVG
def yield_from(node, db):
    return (
        is_single_node(node, ast.Expr)
        and isinstance(node.body[0].value, ast.Yield)
        and target_check(node.body[0].value.value, node.target)
    )


@Inspector.register(ast.FunctionDef)
@Level.HIGH
def default_mutable_arg(node, db):
    return any(isinstance(default, MUTABLE_TYPE) for default in node.args.defaults)
