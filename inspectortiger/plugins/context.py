""" Context change recorder """

__author__ = "Batuhan Taskaya"
__version__ = "1.0.0"

import ast
from dataclasses import dataclass
from enum import Enum, auto

from inspectortiger.inspector import Inspector
from inspectortiger.utils import Events, Level


class Contexts(Enum):
    ANON = auto()  # comps + lambda
    CLASS = auto()
    GLOBAL = auto()
    FUNCTION = auto()


CTX_TYPES = {ast.ClassDef: Contexts.CLASS, ast.FunctionDef: Contexts.FUNCTION}


@dataclass
class Context:
    name: str
    context: Contexts


def change_context(db, name, context):
    db["previous_contexts"].append(db["context"])
    db["context"] = Context(name, context)


@Inspector.register(ast.Module)
def prepare_contexts(node, db):
    db["previous_contexts"] = []
    db["next_contexes"] = {}
    db["context"] = Context("__main__", Contexts.GLOBAL)
    for possible_context in node.body:
        if isinstance(possible_context, tuple(CTX_TYPES)):
            ctx = CTX_TYPES[type(possible_context)]
            ctx = Context(possible_context.name, ctx)
            db["next_contexes"][
                (possible_context.lineno, possible_context.end_lineno)
            ] = ctx


@Inspector.register(ast.ClassDef)
@Level.WATCHER
def context_change(node, db):
    change_context(db, node.name, Contexts.CLASS)


@Inspector.register(ast.FunctionDef)
@Level.WATCHER
def context_change(node, db):
    change_context(db, node.name, Contexts.FUNCTION)
