import ast
import importlib
import tokenize
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from contextlib import suppress
from dataclasses import asdict

from inspectortiger.inspector import Inspector


class PluginLoadError(Exception):
    pass


def inspect(file):
    inspector = Inspector(file)
    with tokenize.open(file) as f:
        content = f.read()
    inspector.visit(ast.parse(content))
    return inspector.results


def inspector(files, workers, ignore):
    all_reports = defaultdict(list)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for inspection in executor.map(inspect, set(files)):
            for plugin, reports in inspection.items():
                all_reports[plugin].extend(
                    asdict(report)
                    for report in reports
                    if report.code not in ignore
                )
    return all_reports


def load_plugins(manager, whitelist=None):
    namespaces = manager.discover()
    for namespace, plugins in namespaces.items():
        for plugin_name, plugin in plugins.items():
            if whitelist and plugin not in whitelist:
                return
            try:
                module = importlib.import_module(f"{namespace}.{plugin}")
                for handler in dir(module):
                    handler = getattr(module, handler)
                    with suppress(AttributeError):
                        handler.plugin = plugin
            except ImportError:
                raise PluginLoadError(
                    f"Couldn't load '{plugin_name.title()}' from `{namespace}` namespace"
                )
