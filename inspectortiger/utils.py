import ast
import sys
from enum import Enum, IntEnum, auto
from functools import lru_cache

_CONSTANT_TYPES = {"Num", "Str", "Bytes", "NameConstant", "Ellipsis"}


class Events(Enum):
    INITAL = auto()
    FINAL = auto()
    NODE_FINALIZE = auto()
    TREE_TRANSFORMER = auto()


class Priority(IntEnum):
    FIRST = 0
    AVG = 1
    LAST = 2

    def __call__(self, func):
        func.priority = self
        return func


def traverse_paths(paths):
    files = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)

        if path.is_file():
            files.append(path)
        else:
            files.extend(path.glob("**/*.py"))
    return files


def mark(func):
    func._inspection_mark = True


@lru_cache(128)
def _version_node(node):
    version = sys.version_info
    if version >= (3, 8) and node in _CONSTANT_TYPES:
        return False
    return True


def is_single_node(a, b):
    return len(a.body) == 1 and isinstance(a.body[0], b)


def name_check(a, *b):
    return isinstance(a, ast.Name) and a.id in b


def constant_check(a, *b):
    return isinstance(a, ast.Constant) and a.value in b


def biname_check(a, b):
    return isinstance(a, ast.Name) and isinstance(b, ast.Name) and a.id == b.id


def tuple_check(a, b):
    if not (isinstance(a, ast.Tuple) and isinstance(b, ast.Tuple)):
        return False
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
