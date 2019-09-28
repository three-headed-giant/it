"""
### Unimport
`unimport` integration to InspectorTiger

- `db['unimport']` => A list of imports that are not used
- Checks if an import is not used through `unimport`
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
    for unused in db["unimport"]:
        if unused["lineno"] == node.lineno:
            return True
