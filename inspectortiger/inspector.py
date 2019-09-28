import ast
from collections import defaultdict
from functools import partial

from reportme.reporter import Requirement
from reportme.reports import Approach

from inspectortiger.utils import Events, Priority


class Inspector(ast.NodeVisitor):

    _hooks = defaultdict(list)
    _event_hooks = defaultdict(list)

    def __init__(self, file, *args, **kwargs):
        self.file = file
        self._hook_db = defaultdict(dict)
        self.results = defaultdict(list)

        for initalizer in self._event_hooks[Events.INITAL]:
            initalizer(self._hook_db)

        super().__init__(*args, **kwargs)

    @classmethod
    def register(cls, *triggerer):
        def wrapper(func):
            nonlocal triggerer
            if len(triggerer) == 1:
                (triggerer,) = triggerer

            if isinstance(triggerer, type) and issubclass(triggerer, ast.AST):
                hooks = cls._hooks[triggerer]
            elif isinstance(triggerer, Events):
                hooks = cls._event_hooks[triggerer]
            else:
                raise ValueError(f"Unsupported triggerer, {triggerer!r}")
            hooks.append(func)
            return func

        return wrapper

    def visitor(self, hooks, node):
        hooks.sort(key=lambda hook: getattr(hook, "priority", Priority.AVG))
        for hook in hooks:
            if hook(node, self._hook_db):
                req_type = getattr(Approach, hook.__name__.upper())()
                self.results[hook.report_level].append(
                    Requirement(self.file, node.lineno, req_type)
                )

        self.generic_visit(node)
        for node_finalizer in self._event_hooks[Events.NODE_FINALIZE, type(node)]:
            node_finalizer(node, self._hook_db)

    def __getattr__(self, attr):
        _attr = attr.strip("visit_")
        if hasattr(ast, _attr):
            return partial(self.visitor, self._hooks[getattr(ast, _attr)])
        raise AttributeError(attr)
