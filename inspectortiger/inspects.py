import importlib


class PluginLoadError(Exception):
    pass


def load_plugins(manager):
    namespaces = manager.discover()
    for namespace, plugins in namespaces.items():
        for plugin_name, plugin in plugins.items():
            try:
                importlib.import_module(f"{namespace}.{plugin}")
            except ImportError:
                raise PluginLoadError(
                    f"Couldn't load '{plugin_name.title()}' from `{namespace}` namespace"
                )
