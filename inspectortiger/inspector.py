import ast
from collections import defaultdict
from functools import partial

from inspectortiger.reports import Report
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
            trigger = triggerer[0]
            if isinstance(trigger, type) and issubclass(trigger, ast.AST):
                hooks = cls._hooks[trigger]
            elif isinstance(trigger, Events):
                if len(triggerer) > 1:
                    hooks = cls._event_hooks[triggerer]
                else:
                    hooks = cls._event_hooks[trigger]
            else:
                raise ValueError(f"Unsupported triggerer, {triggerer!r}")
            hooks.append(func)
            return func

        return wrapper

    def visitor(self, hooks, node):
        hooks.sort(key=lambda hook: getattr(hook, "priority", Priority.AVG))
        for hook in hooks:
            if hook(node, self._hook_db):
                code = hook.__name__.upper()
                plugin = getattr(hook, "plugin", "unknown")
                report = Report(code, node.lineno, str(self.file))
                self.results[plugin].append(report)

        self.generic_visit(node)
        for node_finalizer in self._event_hooks[Events.NODE_FINALIZE]:
            node_finalizer(node, self._hook_db)

    def __getattr__(self, attr):
        _attr = attr.strip("visit_")
        if hasattr(ast, _attr):
            return partial(self.visitor, self._hooks[getattr(ast, _attr)])
        raise AttributeError(attr)
