import ast
from collections import defaultdict
from enum import Enum, auto
from itertools import chain

if __debug__:
    from astpretty import pprint

PSEUDO_LEVELS = {"watcher", "disabled"}


class Level(Enum):
    EXTREME_LOW = auto()
    LOW = auto()
    AVG = auto()
    HIGH = auto()
    EXTREME_HIGH = auto()

    WATCHER = auto()
    DISABLED = auto()

    def __call__(self, func):
        func.report_level = self
        return func


class Events(Enum):
    INITAL = auto()
    FINAL = auto()


def is_single_node(a, b):
    return len(a.body) == 1 and isinstance(a.body[0], b)


def name_check(a, *b):
    return isinstance(a, ast.Name) and a.id in b


def biname_check(a, b):
    return isinstance(a, ast.Name) and isinstance(b, ast.Name) and a.id == b.id


def tuple_check(a, b):
    if len(a.elts) != len(b.elts):
        return False
    for aside_element, bside_element in zip(a.elts, b.elts):
        if not biname_check(aside_element, bside_element):
            break
    else:
        return True
    return False


def target_check(a, b):
    if type(a) != type(b):
        return False
    if isinstance(a, ast.Name) and biname_check(a, b):
        return True
    elif isinstance(a, ast.Tuple) and tuple_check(a, b):
        return True
    else:
        return False
