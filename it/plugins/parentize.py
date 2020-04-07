"""
## Parentize
`parent` field to each node

- `parent_to(child, node)` => yields all parents of child until it reaches `node`
"""
import ast
import weakref

from it.inspector import Inspector
from it.utils import Events

__author__ = "Batuhan Taskaya"
WEAK = False


@Inspector.on_event(Events.TREE_TRANSFORMER)
def parentize(tree, db):
    for parent in ast.walk(tree):
        for children in ast.iter_child_nodes(parent):
            if WEAK:
                ref = weakref.ref(parent)
            else:
                ref = parent
            children.parent = ref
    return tree


def parent_to(child, parent):
    if not hasattr(child, "parent"):
        raise ValueError(
            "Node should have `parent` reference created by `it.plugins.parentize`"
        )

    current = child.parent
    while current is not parent:
        yield current
        current = current.parent
    yield parent
