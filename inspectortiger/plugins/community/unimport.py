"""
### Unimport
`unimport` integration

- `db['unimport']` => A list of imports that are not used
"""

__author__ = "Batuhan Taskaya"

import ast

from unimport.unused import get_unused

from inspectortiger.inspector import Inspector


@Inspector.register(ast.Module)
def set_unimport(node, db):
    db["unimport"] = get_unused(node)


@Inspector.register(ast.Import, ast.ImportFrom)
def unused_import(node, db):
    """A module/name is imported but not used."""
    for unused in db["unimport"]:
        if unused["lineno"] == node.lineno:
            return True
