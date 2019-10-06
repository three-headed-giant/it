import ast
import tokenize
from collections import defaultdict
from dis import Bytecode
from functools import partial

from inspectortiger.configmanager import logger
from inspectortiger.reports import Report
from inspectortiger.utils import Events, Priority


class Inspector(ast.NodeVisitor):

    _hooks = defaultdict(list)
    _event_hooks = defaultdict(list)

    def __init__(self, source, *args, **kwargs):
        if isinstance(source, ast.AST):
            self.file = "<unknown>"
            self.source = source
        else:
            self.file = source
            self.source = None

        self._hook_db = defaultdict(partial(defaultdict, dict))
        self.results = defaultdict(list)
        self.sort_hooks()

        for initalizer in self._event_hooks[Events.INITAL]:
            initalizer(self._hook_db)

        super().__init__(*args, **kwargs)

        if not self.source:
            with tokenize.open(self.file) as f:
                self.source = f.read()

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

    def sort_hooks(self):
        def priority(hook):
            return getattr(hook, "priority", Priority.AVG)

        for hooks in self._hooks.values():
            hooks.sort(key=priority)

        for event_hooks in self._event_hooks.values():
            event_hooks.sort(key=priority)

    def visitor(self, hooks, node):
        for hook in hooks:
            logger.debug("Visiting {type(node).__name__}.")
            if hook(node, self._hook_db):
                code = hook.__name__.upper()
                plugin = getattr(hook, "plugin", "unknown")
                report = Report(code, node.lineno, str(self.file))
                self.results[plugin.plugin].append(report)

        self.generic_visit(node)
        for node_finalizer in self._event_hooks[Events.NODE_FINALIZE]:
            if isinstance(node, tuple(node_finalizer.handles)):
                node_finalizer(node, self._hook_db)

    def handle(self):
        tree = ast.parse(self.source, self.file)
        for tree_transformer in self._event_hooks[Events.TREE_TRANSFORMER]:
            tree = tree_transformer(tree, self._hook_db)
        self.visit(tree)

    def __getattr__(self, attr):
        _attr = attr[len("visit_") :]
        if hasattr(ast, _attr):
            return partial(self.visitor, self._hooks[getattr(ast, _attr)])
        raise AttributeError(attr)
