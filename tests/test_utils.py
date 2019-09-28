import ast

from inspectortiger.utils import (
    biname_check,
    is_single_node,
    name_check,
    target_check,
    tuple_check,
)


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
