import importlib
from contextlib import suppress


class PluginLoadError(Exception):
    pass


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
