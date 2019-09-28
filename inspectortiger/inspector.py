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
    def register(cls, *nodes):
        def wrapper(func):
            handles = set(nodes)
            if hasattr(func, "handles"):
                func.handles.update(handles)
            else:
                func.handles = handles

            for node in nodes:
                cls._hooks[node].append(func)
            return func

        return wrapper

    @classmethod
    def on_event(cls, *events):
        def wrapper(func):
            if hasattr(func, "handles"):
                for handle in func.handles:
                    cls._hooks[handle].remove(func)
            for event in events:
                cls._event_hooks[event].append(func)
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
            if isinstance(node, tuple(node_finalizer.handles)):
                node_finalizer(node, self._hook_db)

    def __getattr__(self, attr):
        _attr = attr.strip("visit_")
        if hasattr(ast, _attr):
            return partial(self.visitor, self._hooks[getattr(ast, _attr)])
        raise AttributeError(attr)
