""" Unimport integration """

__author__ = "Batuhan Taskaya"
__requires__ = ["unimport"]

import ast

from unimport import UnImport

from inspectortiger.inspector import Inspector


@Inspector.register(ast.Module)
def set_unimport(node, db):
    db["unimport"] = UnImport(node)


@Inspector.register(ast.Import, ast.ImportFrom)
def unused_import(node, db):
    for unused in db["unimport"].get_diff():
        if unused["lineno"] == node.lineno:
            return True
