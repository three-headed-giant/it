import ast
import sys

import pytest

from inspectortiger.utils import (
    Priority,
    biname_check,
    constant_check,
    is_single_node,
    mark,
    name_check,
    target_check,
    tuple_check,
)


def test_priority():
    dummy = lambda: None
    first = Priority.FIRST
    first(dummy)
    assert hasattr(dummy, "priority")
    assert dummy.priority is first
    Priority.LAST(dummy)
    assert dummy.priority is Priority.LAST


def test_mark():
    dummy = lambda: None
    mark(dummy)
    assert hasattr(dummy, "_inspection_mark")
    assert dummy._inspection_mark


def test_is_single_node():
    assert is_single_node(ast.parse("a = 1"), ast.Assign)
    assert not is_single_node(ast.parse("a = 1"), ast.AnnAssign)
    assert not is_single_node(ast.parse("a = 1;b = 2"), ast.Assign)


def test_name_check():
    name = ast.parse("var", "<ast>", "eval")
    assert name_check(name.body, "var")
    assert name_check(name.body, "tar", "car", "var")
    assert not name_check(name.body, "car")
    assert not name_check(name, "var")


@pytest.mark.parametrize("constant", (1, '"a"', 1.7, True, None, False))
def test_constant_check(constant):
    node = ast.parse(str(constant), "<ast>", "eval").body
    constant = ast.literal_eval(node)
    assert constant_check(node, constant)
    assert constant_check(node, 3, 5, "xxx", constant)
    assert not constant_check(node, 3, 5)
    assert not constant_check(ast.Pass(), 3, 5)


_EDGE_CONSTANTS = {"1", "0", "True", "False", "1.0", "0.0"}


@pytest.mark.parametrize("constant", _EDGE_CONSTANTS)
def test_constant_check_edge(constant):
    node = ast.parse(str(constant), "<ast>", "eval").body
    constant = ast.literal_eval(node)
    not_same_constants = _EDGE_CONSTANTS - {str(constant)}
    for not_same_constant in not_same_constants:
        not_same_constant = ast.literal_eval(not_same_constant)
        assert not constant_check(node, not_same_constant)
    assert constant_check(node, constant)


def test_biname_check():
    name = ast.parse("var", "<ast>", "eval")
    assert biname_check(name.body, name.body)
    assert biname_check(name.body, ast.Name("var"))
    assert not biname_check(name.body, ast.Name("car"))
    assert not biname_check(ast.Expression(), ast.Expression())


def test_tuple_check():
    mytuple = ast.parse("a, b, c", "<ast>", "eval").body
    assert tuple_check(mytuple, mytuple)
    assert tuple_check(
        mytuple, ast.Tuple([ast.Name("a"), ast.Name("b"), ast.Name("c")])
    )
    assert not tuple_check(
        mytuple, ast.Tuple([ast.Name("a"), ast.Name("c"), ast.Name("b")])
    )
    assert not tuple_check(mytuple, ast.Expression())
    assert not tuple_check(mytuple, ast.Tuple([ast.Name("a"), ast.Name("b")]))


def test_target_check():
    mytarget_1 = ast.parse("a", "<ast>", "eval").body
    mytarget_2 = ast.parse("a, b, c", "<ast>", "eval").body
    assert target_check(mytarget_1, mytarget_1)
    assert target_check(mytarget_2, mytarget_2)
    assert not target_check(mytarget_1, mytarget_2)
    assert not target_check(ast.Expression(), ast.Expression())
