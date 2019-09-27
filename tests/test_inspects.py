import pytest

from inspectortiger.inspects import PluginLoadError, load_plugins


@pytest.fixture
def manager():
    class Manager:
        def discover(self):
            return {"namespace": {"plugin name": "plugin"}}

    return Manager()


def test_load_plugins(manager, mocker):
    import_module = mocker.patch("importlib.import_module")
    load_plugins(manager)
    import_module.assert_called_with("namespace.plugin")


def test_load_plugins_invalid(manager, mocker):
    import_module = mocker.patch("importlib.import_module")
    import_module.side_effect = ImportError
    with pytest.raises(PluginLoadError):
        load_plugins(manager)
