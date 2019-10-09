import ast
from dataclasses import asdict

import pytest

from inspectortiger.config_manager import Plugin
from inspectortiger.inspector import Inspector
from inspectortiger.inspects import inspect, inspector, load_plugins
from inspectortiger.reports import Report


@pytest.fixture
def clear_inspector():
    Inspector._hooks.clear()
    Inspector._event_hooks.clear()


def register_dummy():
    dummy = lambda *args: True
    dummy.__name__ = "my_error"
    dummy.plugin = Plugin.from_simple("@dummy")
    Inspector.register(ast.Module)(dummy)


def test_inspect(tmp_path, clear_inspector):
    some_file = tmp_path / "___.py"
    some_file.write_text("# some file with no code")
    assert inspect(some_file) == {}
    register_dummy()
    assert inspect(some_file) == {
        "dummy": [
            Report(
                code="MY_ERROR", column=0, lineno=0, filename=str(some_file)
            )
        ]
    }


def test_inspector(tmp_path, clear_inspector):
    files = []
    for idx in range(10):
        file = tmp_path / f"file{idx},py"
        file.write_text("# some file with no code")
        files.append(file)
        if idx % 2 == 0:
            files.append(file)

    assert inspector(files, 2, set()) == {}
    register_dummy()

    assert inspector(files, 2, set()) == {
        "dummy": [
            asdict(Report("MY_ERROR", 0, 0, str(file))) for file in set(files)
        ]
    }
    assert inspector(files, 2, set()) == inspector(set(files), 2, set())
    assert inspector(files, 2, {"MY_ERROR"}) == {}
