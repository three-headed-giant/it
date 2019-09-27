""" Unimport integration """

__author__ = "Batuhan Taskaya"
__requires__ = ["unimport"]

import ast

from unimport import UnImport

from inspectortiger.inspector import Inspector
from inspectortiger.utils import Level


@Inspector.register(ast.Module)
@Level.WATCHER
def set_unimport(node, db):
    db["unimport"] = UnImport(node)


@Inspector.register(ast.Import)
@Inspector.register(ast.ImportFrom)
@Level.LOW
def unused_import(node, db):
    for unused in db["unimport"].get_diff():
        if unused["lineno"] == node.lineno:
            return True
