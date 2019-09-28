""" Context management plugin

db["context"] => A context instance that gives current context
db["previous_contexts"] => A list of previous contexts
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum, auto
from pprint import pprint

from inspectortiger.inspector import Inspector
from inspectortiger.utils import Events

__author__ = "Batuhan Taskaya"


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
    kpair: KPair


@dataclass(unsafe_hash=True)
class KPair:
    start: int
    end: int

    @classmethod
    def from_node(cls, node):
        return cls(start=node.lineno, end=node.end_lineno)

    def distance(self, other):
        return ((self.start - other.start) ** 2 + (self.end - other.end) ** 2) ** 0.5


def get_context(node, db):
    possible_contexts = []
    node_kpair = KPair.from_node(node)
    for kpair, context in db["next_contexts"].items():
        if node_kpair.start >= kpair.start and node_kpair.end <= kpair.end:
            possible_contexts.append((kpair.distance(node_kpair), context))

    possible_contexts.sort(key=lambda ctx: ctx[0])
    return possible_contexts[0][1]


@Inspector.register(ast.Module)
def prepare_contexts(node, db):
    db["global_ctx"] = global_ctx = Context("__main__", Contexts.GLOBAL, KPair(0, 0))
    db["previous_contexts"] = []
    db["context"] = global_ctx
    for possible_context in ast.walk(node):
        if isinstance(possible_context, tuple(CTX_TYPES)):
            kpair = KPair.from_node(possible_context)
            ctx = CTX_TYPES[type(possible_context)]
            ctx = Context(possible_context.name, ctx, kpair)
            db["next_contexts"][ctx.kpair] = ctx


@Inspector.register(ast.ClassDef, ast.FunctionDef)
def change_context(node, db):
    context = get_context(node, db)
    db["previous_contexts"].append(db["context"])
    db["context"] = context


@Inspector.on_event(Events.NODE_FINALIZE)
@Inspector.register(ast.ClassDef, ast.FunctionDef)
def finalize_context(node, db):
    context = db["previous_contexts"].pop()
    db["context"] = context
