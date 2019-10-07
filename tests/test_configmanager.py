from inspectortiger.configmanager import (
    Blacklist,
    Config,
    ConfigManager,
    Plugin,
    PluginLoadError,
    _Plugin,
)


def test_plugin_metaclass():
    MyPlugin = _Plugin("My Plugin", (), {"__init__": lambda *args: None})
    assert MyPlugin(1, 2) is MyPlugin(1, 2)
    assert MyPlugin(1, 3) is not MyPlugin(1, 4)

    first = MyPlugin(1, 5)
    first.active = True
    assert MyPlugin(1, 5).active


def test_plugin_init():
    package = Plugin("b", "a")
    assert package.plugin == "b" and package.namespace == "a"
    assert package.static_name == "a.b"
    sub_package = Plugin("c", "a.b")
    assert sub_package.plugin == "c" and sub_package.namespace == "a.b"
    assert sub_package.static_name == "a.b.c"
    sub_sub_package = Plugin("d", "a.b.c")
    assert (
        sub_sub_package.plugin == "d" and sub_sub_package.namespace == "a.b.c"
    )
    assert sub_sub_package.static_name == "a.b.c.d"


def test_plugin_from_simple():
    assert Plugin.from_simple("a.b") is Plugin("b", "a")
    assert Plugin.from_simple("a.b.c") is Plugin("c", "a.b")
    assert Plugin.from_simple("a.b.c.d") is Plugin("d", "a.b.c")

    core_package = Plugin.from_simple("@context")
    assert (
        core_package.plugin == "context"
        and core_package.namespace == "inspectortiger.plugins"
    )
    sub_core_package = Plugin.from_simple("@community.unimport")
    assert (
        sub_core_package.plugin == "unimport"
        and sub_core_package.namespace == "inspectortiger.plugins.community"
    )


def test_plugin_from_config():
    plugins = Plugin.from_config(dict(a=["b", "c.d"]))
    assert isinstance(plugins, list)
    assert plugins[0] is Plugin("b", "a")
    assert plugins[1] is Plugin("d", "a.c")
    multiple_namespace_plugins = Plugin.from_config(dict(a=["b"], c=["d.e"]))
    assert multiple_namespace_plugins[0] is Plugin("b", "a")
    assert multiple_namespace_plugins[1] is Plugin("e", "c.d")
