"""
### Unimport
`unimport` integration

- `db["community"]["unimport"]["unimport"]` => A list of imports that are not used
"""

__author__ = "Batuhan Taskaya"

import ast

from unimport.unused import get_unused

from inspectortiger.inspector import Inspector


@Inspector.register(ast.Module)
def set_unimport(node, db):
    db["community"]["unimport"]["unimport"] = get_unused(node)


@Inspector.register(ast.Import, ast.ImportFrom)
def unused_import(node, db):
    """A module/name is imported but not used."""
    for unused in db["community"]["unimport"]["unimport"]:
        if unused["lineno"] == node.lineno:
            return True
