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


@dataclass
class Context:
    name: str
    context: Contexts


def change_context(db, name, context):
    db["previous_contexts"].append(db["context"])
    db["context"] = Context(name, context)


@Inspector.register(Events.INITAL)
def prepare_contexts(db):
    db["previous_contexts"] = []
    db["context"] = Context("__main__", Contexts.GLOBAL)


@Inspector.register(ast.ClassDef)
@Level.WATCHER
def context_change(node, db):
    change_context(db, node.name, Contexts.CLASS)


@Inspector.register(ast.FunctionDef)
@Level.WATCHER
def context_change(node, db):
    change_context(db, node.name, Contexts.FUNCTION)
