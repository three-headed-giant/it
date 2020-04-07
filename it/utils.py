import ast
import logging
import sys
from enum import Enum, IntEnum, auto
from functools import lru_cache
from pathlib import Path

PY39_PLUS = sys.version_info >= (3, 9)
PY38_PLUS = sys.version_info >= (3, 8)
PY38_MINUS = not PY38_PLUS

USER_CONFIG = Path("~/.inspector.rc").expanduser()
PROJECT_CONFIG = Path(".inspector.rc")
logger = logging.getLogger("it")

_CONSTANT_TYPES = {"Num", "Str", "Bytes", "NameConstant", "Ellipsis"}
_PSEUDO_FIELDS = {"cls", "__class__"}


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


class Group(Enum):
    CODE = auto()
    PLUGIN = auto()
    COLUMN = auto()
    LINENO = auto()
    FILENAME = auto()


def prepare_logger(
    logging_handler_level=logging.INFO, logging_level=logging.INFO
):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging_handler_level)
    logger.setLevel(logging_level)

    formatter = logging.Formatter(
        "[Inspector Tiger] %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


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
    if PY38_PLUS and node in _CONSTANT_TYPES:
        return False
    return True


def is_single_node(a, b):
    return len(a.body) == 1 and isinstance(a.body[0], b)


def name_check(a, *b):
    return isinstance(a, ast.Name) and a.id in b


def constant_check(a, *b):
    if PY38_PLUS and isinstance(a, ast.Constant):
        constant_value = a.value
    elif PY38_MINUS and isinstance(a, (ast.Str, ast.Bytes)):
        constant_value = a.s
    elif PY38_MINUS and isinstance(a, ast.Num):
        constant_value = a.n
    elif PY38_MINUS and isinstance(a, ast.Ellipsis):
        constant_value = Ellipsis
    elif PY38_MINUS and isinstance(a, ast.NameConstant):
        constant_value = a.value
    else:
        return False

    possible_types = {(type(x), x) for x in b}
    return (type(constant_value), constant_value) in possible_types


@lru_cache(1)
def get_slice(a):
    if PY39_PLUS:
        return a.slice
    else:
        return a.slice.value


def version_bound_check(node, base, flag):
    if flag:
        return True
    else:
        return isinstance(node, getattr(ast, base))


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


def ismarked(a):
    return getattr(a, "_inspection_mark", False)
