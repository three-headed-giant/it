""" Context management plugin

db["context"] => A context instance that gives current context
db["previous_contexts"] => A list of previous contexts
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum, auto

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
        return cls(start=node.lineno, end=node.lineno)

    def distance(self, other):
        return ((self.start - other.start) ** 2 + (self.end - other.end) ** 2) ** 0.5


def get_context(node, next_contexts):
    possible_contexts = []
    node_kpair = KPair.from_node(node)
    for kpair, context in next_contexts.items():
        if node_kpair.start >= kpair.start and node_kpair.end <= kpair.end:
            possible_contexts.append((kpair.distance(node_kpair), context))

    possible_contexts.sort(key=lambda ctx: ctx[0])
    if possible_contexts:
        context = possible_contexts[0][1]
    else:
        context = Context("__main__", Contexts.GLOBAL, KPair(0, 0))
    return context


@Inspector.register(ast.Module)
def prepare_contexts(node, db):
    db["previous_contexts"] = []
    db["context"] = Context("__main__", Contexts.GLOBAL, KPair(0, 0))
    for possible_context in ast.walk(node):
        if isinstance(possible_context, tuple(CTX_TYPES)):
            kpair = KPair.from_node(possible_context)

            ctx = CTX_TYPES[type(possible_context)]
            ctx = Context(possible_context.name, ctx, kpair)
            db["next_contexts"][ctx.kpair] = ctx


@Inspector.register(ast.FunctionDef)
@Inspector.register(ast.ClassDef)
def change_context(node, db):
    context = get_context(node, db["next_contexts"])
    db["previous_contexts"].append(db["context"])
    db["context"] = context


@Inspector.register(Events.NODE_FINALIZE, ast.FunctionDef)
@Inspector.register(Events.NODE_FINALIZE, ast.ClassDef)
def finalize_context(node, db):
    context = db["previous_contexts"].pop()
    db["context"] = context
