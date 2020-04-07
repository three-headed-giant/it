import ast
import tokenize
from collections import defaultdict
from contextlib import contextmanager, suppress
from functools import lru_cache, partial

from it.reports import Report
from it.utils import Events, Priority, _version_node, logger, mark

with suppress(ImportError):
    import conast_fast  # https://github.com/thg-consulting/conast

    ast.iter_fields = conast.fields
    ast.iter_child_nodes = conast.child_nodes
    ast.walk = conast.walk
    ast.NodeVisitor = conast.NodeVisitor


class BufferExit(Exception):
    pass


class Inspector(ast.NodeVisitor):

    _hooks = defaultdict(list)
    _event_hooks = defaultdict(list)

    _hooks_buffer = defaultdict(list)
    _event_hooks_buffer = defaultdict(list)

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
            mark(func)

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
            mark(func)
            if hasattr(func, "handles"):
                for handle in func.handles:
                    with suppress(ValueError):
                        cls._hooks[handle].remove(func)
            for event in events:
                cls._event_hooks[event].append(func)
            return func

        return wrapper

    @classmethod
    @contextmanager
    def buffer(cls):
        append = True
        hooks, events = cls._hooks, cls._event_hooks
        try:
            cls._hooks, cls._event_hooks = (
                cls._hooks_buffer,
                cls._event_hooks_buffer,
            )
            yield
        except BufferExit:
            append = False
        finally:
            if append:
                for trigger, _hooks in cls._hooks.items():
                    hooks[trigger].extend(_hooks)
                for trigger, _hooks in cls._event_hooks.items():
                    events[trigger].extend(_hooks)

            cls._hooks, cls._event_hooks = hooks, events
            cls._hooks_buffer.clear()
            cls._event_hooks_buffer.clear()

    def sort_hooks(self):
        def priority(hook):
            return getattr(hook, "priority", Priority.AVG)

        for hooks in (*self._hooks.values(), *self._event_hooks.values()):
            for hook in hooks:
                if hasattr(hook, "requires"):
                    if any(require.inactive for require in hook.requires):
                        hooks.remove(hook)
            hooks.sort(key=priority)

    def visitor(self, hooks, node):
        for hook in hooks:
            logger.debug("Visiting {type(node).__name__}.")
            if hook(node, self._hook_db):
                code = hook.__name__.upper()
                plugin = getattr(hook, "plugin", "unknown")
                if not hasattr(node, "lineno"):
                    node.lineno = 0
                    node.col_offset = 0

                report = Report(
                    code, node.col_offset, node.lineno, str(self.file)
                )
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
        return self.results

    @lru_cache(128)
    def __getattr__(self, attr):
        _attr = attr[len("visit_") :]
        if hasattr(ast, _attr) and _version_node(_attr):
            return partial(self.visitor, self._hooks[getattr(ast, _attr)])
        raise AttributeError(attr)
