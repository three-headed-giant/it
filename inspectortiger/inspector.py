import ast
from collections import defaultdict
from functools import partial

from astpretty import pprint

from inspectortiger.utils import is_single_node, target_check
from reportme.reporter import Requirement
from reportme.reports import Approach

MUTABLE_TYPE = (ast.List, ast.Dict, ast.Set)


class Inspector(ast.NodeVisitor):

    _hooks = defaultdict(list)

    def __init__(self, file, *args, **kwargs):
        self.file = file
        self._hook_db = defaultdict(dict)
        self.results = []
        super().__init__(*args, **kwargs)

    @classmethod
    def register(cls, node):
        def wrapper(func):
            cls._hooks[node].append(func)
            return func

        return wrapper

    def wrapper(self, hooks, node):
        for hook in hooks:
            if hook(node, self._hook_db):
                req_type = getattr(Approach, hook.__name__.upper())()
                self.results.append(Requirement(self.file, node.lineno, req_type))
        return self.generic_visit(node)

    def __getattr__(self, attr):
        _attr = attr.strip("visit_")
        if hasattr(ast, _attr):
            return partial(self.wrapper, self._hooks[getattr(ast, _attr)])
        raise AttributeError(attr)


@Inspector.register(ast.For)
def yield_from(node, db):
    return (
        is_single_node(node, ast.Expr)
        and isinstance(node.body[0].value, ast.Yield)
        and target_check(node.body[0].value.value, node.target)
    )


@Inspector.register(ast.FunctionDef)
def default_mutable_arg(node, db):
    return any(isinstance(default, MUTABLE_TYPE) for default in node.args.defaults)
