import ast
from astpretty import pprint
from collections import defaultdict
from functools import partial
from inspectortiger.utils import is_single_node, target_check
from reportme.reports import Approach

class Inspector(ast.NodeVisitor):

    _hooks = defaultdict(list)

    def __init__(self, *args, **kwargs):
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
        if not hooks:
            return self.generic_visit(node)

        for hook in hooks:
            result = hook(node, self._hook_db)
            if result:
                self.results.append(result)

    def __getattr__(self, attr):
        _attr = attr.strip("visit_")
        if hasattr(ast, _attr):
            return partial(self.wrapper, self._hooks[getattr(ast, _attr)])
        raise AttributeError(attr)


@Inspector.register(ast.For)
def yield_from(node, db):
    if (
        is_single_node(node, ast.Expr)
        and isinstance(node.body[0].value, ast.Yield)
        and target_check(node.body[0].value.value, node.target)
    ):
        pass
