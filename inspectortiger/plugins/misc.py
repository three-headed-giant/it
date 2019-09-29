"""
## Misc
Common gotchas

"""

__author__ = "Batuhan Taskaya"

import ast

from inspectortiger.inspector import Inspector

MUTABLE_TYPE = (ast.List, ast.Dict, ast.Set)


@Inspector.register(ast.FunctionDef)
def default_mutable_arg(node, db):
    """Default argument is something mutable."""

    return any(
        isinstance(default, MUTABLE_TYPE) for default in node.args.defaults
    )
