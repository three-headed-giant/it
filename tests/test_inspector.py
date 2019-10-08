import ast

import pytest

from inspectortiger import Inspector
from inspectortiger.config_manager import Plugin
from inspectortiger.inspector import BufferExit


@pytest.fixture
def clear():
    Inspector._hooks.clear()
    Inspector._event_hooks.clear()
    Inspector._hooks_buffer.clear()
    Inspector._event_hooks_buffer.clear()


@pytest.fixture
def dummy():
    dummy = lambda *args: True
    dummy.__name__ = "my_error"
    dummy.plugin = Plugin.from_simple("@dummy")
    return dummy


def test_inspector_register(clear, dummy):
    Inspector.register(1)(dummy)
    assert dummy.handles == {1}
    assert Inspector._hooks[1] == [dummy]
    assert dummy._inspection_mark

    Inspector.register(2, 3)(dummy)
    assert dummy.handles == {1, 2, 3}
    for hook in range(1, 4):
        assert Inspector._hooks[hook] == [dummy]
    assert dummy._inspection_mark


def test_inspector_on_event(clear, dummy):
    Inspector.on_event(1)(dummy)
    assert Inspector._event_hooks[1] == [dummy]
    assert dummy._inspection_mark

    Inspector.on_event(2, 3)(dummy)
    for hook in range(1, 4):
        assert Inspector._event_hooks[hook] == [dummy]
    assert dummy._inspection_mark

    Inspector.register(4, 5)(dummy)
    Inspector.on_event(6, 7, 8)(dummy)
    assert Inspector._hooks == {4: [], 5: []}


def test_inspector_buffer(clear, dummy):
    with Inspector.buffer():
        Inspector.register(1)(dummy)
        Inspector.on_event(2, 3)(dummy)
        raise BufferExit

    assert Inspector._hooks == Inspector._event_hooks == {}

    with Inspector.buffer():
        Inspector.register(4)(dummy)

    assert dummy in Inspector._hooks[4]


def test_inspector_getattr(clear, dummy):
    Inspector.register(ast.Name)(dummy)

    inspector = Inspector(ast.Module())
    visitor = inspector.visit_Name
    assert visitor.func == inspector.visitor
    assert dummy in visitor.args[0]

    with pytest.raises(AttributeError):
        inspector.duhkjhkjdsabc
