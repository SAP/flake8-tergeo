"""Tests for _flake8_tergeo.ast_util."""

from __future__ import annotations

import ast
import sys
from typing import Any, Union, cast

import pytest
from pytest_mock import MockerFixture

from _flake8_tergeo.ast_util import (
    _get_import_map,
    _iter_child_nodes,
    get_imports,
    get_line_range,
    get_parent,
    get_parent_info,
    in_annotation,
    is_constant_node,
    is_in_type_alias,
    is_in_type_statement,
    is_stub,
    set_info_in_tree,
    stringify,
)


def test_parents() -> None:
    tree = ast.parse(
        """
class Foo:
    def bar():
        a = 1
        return a
    """
    )
    set_info_in_tree(tree)

    assert not get_parent(tree)
    assert not get_parent_info(tree)

    assert len(tree.body) == 1
    clazz = tree.body[0]
    assert get_parent(clazz) == tree
    assert get_parent_info(clazz) == ("body", tree)
    assert isinstance(clazz, ast.ClassDef)

    assert len(clazz.body) == 1
    func = clazz.body[0]
    assert get_parent(func) == clazz
    assert get_parent_info(func) == ("body", clazz)
    assert isinstance(func, ast.FunctionDef)

    assert len(func.body) == 2
    assign = func.body[0]
    assert get_parent(assign) == func
    assert get_parent_info(func) == ("body", clazz)
    assert isinstance(assign, ast.Assign)
    assert get_parent(assign.value) == assign
    assert get_parent_info(assign.value) == ("value", assign)

    ret = func.body[1]
    assert get_parent(ret) == func
    assert get_parent_info(func) == ("body", clazz)
    assert isinstance(ret, ast.Return)
    assert ret.value
    assert get_parent(ret.value) == ret
    assert get_parent_info(func) == ("body", clazz)


def test_iter_child_nodes_field_none(mocker: MockerFixture) -> None:
    node = mocker.Mock(spec=ast.AST)
    node._fields = ["foo"]
    node.foo = [None]
    assert not list(_iter_child_nodes(node))


@pytest.mark.parametrize(
    "code,start,end",
    [
        ("foo=1", 1, 1),
        ("def foo(): pass", 1, 1),
        ("def foo():\n  a=1\n  b=2", 1, 3),
        ("@foo\ndef foo():\n  a=1\n  b=2", 1, 4),
        ("@foo(\n  x,\n)\ndef foo():\n  a=1\n  b=2", 1, 6),
    ],
)
def test_get_line_range(code: str, start: int, end: int) -> None:
    tree = ast.parse(code)
    assert len(tree.body) == 1
    assert get_line_range(tree.body[0]) == (start, end)


@pytest.mark.parametrize(
    "signature", ["def foo()", "async def foo()", "def foo(a) -> None"]
)
@pytest.mark.parametrize(
    "body",
    ["...", "pass", " raise ValueError('foo')", "'''foo'''", "\n  '''foo'''\n  pass"],
)
def test_is_stub(signature: str, body: str) -> None:
    func = signature + ":" + body
    tree = ast.parse(func)
    assert is_stub(tree.body[0])  # type:ignore[arg-type]


@pytest.mark.parametrize(
    "code",
    [
        "def foo(): a=1",
        "async def foo(): a=1",
        """
def foo():
    a = 1
    raise Exception
""",
        """
def foo():
    '''foo'''
    a = 1
""",
        """
def foo():
    '''foo'''
    a = 1
    raise Exception
""",
        """
async def foo():
    '''foo'''
    a = 1
    raise Exception
""",
    ],
)
def test_no_stub(code: str) -> None:
    tree = ast.parse(code)
    func = cast(ast.FunctionDef, tree.body[0])
    assert not is_stub(func)


def test_is_constant_node() -> None:
    tree = ast.parse("a=1")
    assign = cast(ast.Assign, tree.body[0])
    constant = cast(ast.Constant, assign.value)

    assert not is_constant_node(None, (int, float))
    assert not is_constant_node(tree, (int, float))
    assert not is_constant_node(constant, str)

    assert is_constant_node(constant, (int, float))
    assert is_constant_node(constant, int)


@pytest.mark.parametrize(
    "code,expected",
    [("foo", "foo"), ("foo.bar", "foo.bar"), ("tokens[index].start", "")],
)
def test_stringify(code: str, expected: str) -> None:
    tree = ast.parse(code)
    expr = cast(ast.Expr, tree.body[0])
    value = cast(Union[ast.Name, ast.Attribute], expr.value)
    assert stringify(value) == expected


def test_get_imports_no_imports() -> None:
    tree = ast.parse("a = 1")
    assert not get_imports(tree)


def test_get_imports() -> None:
    tree = ast.parse(
        """
import foo
from bar import foo

if TYPE_CHECKING:
    import for_checking

def more():
    import m1, m2
    from m3 import x as y
"""
    )
    assert get_imports(tree) == ["bar.foo", "foo", "for_checking", "m1", "m2", "m3.x"]


@pytest.mark.parametrize("code", ["from . import foo", "from .bar import foo"])
def test_get_imports_local_import(code: str) -> None:
    tree = ast.parse(code)
    assert not get_imports(tree)


def test_get_import_map() -> None:
    assert _get_import_map("foo.bar", "baz") == {
        "baz": {"foo.bar.baz"},
        "bar.baz": {"foo.bar"},
        "foo.bar.baz": {"foo", "foo.bar"},
    }
    assert _get_import_map("foo.bar", "baz.xyz") == {
        "baz.xyz": {"foo.bar.baz"},
        "bar.baz.xyz": {"foo.bar"},
        "foo.bar.baz.xyz": {"foo", "foo.bar"},
    }
    assert _get_import_map("foo.bar.baz", "xyz") == {
        "xyz": {"foo.bar.baz.xyz"},
        "baz.xyz": {"foo.bar.baz"},
        "bar.baz.xyz": {"foo.bar"},
        "foo.bar.baz.xyz": {"foo", "foo.bar", "foo.bar.baz"},
    }


def test_get_import_map_with_typing() -> None:
    assert _get_import_map("typing", "Dict") == {
        "Dict": {"typing.Dict", "typing_extensions.Dict"},
        "typing.Dict": {"typing"},
        "typing_extensions.Dict": {"typing_extensions"},
    }


def test_in_annotation_function() -> None:
    tree = ast.parse("def foo(a, b: int, c:int|float|None) -> int|None: pass")
    set_info_in_tree(tree)

    assert not in_annotation(tree)

    func = cast(ast.FunctionDef, tree.body[0])
    assert not in_annotation(func)

    arg1 = func.args.args[0]
    assert not in_annotation(arg1)

    arg2 = func.args.args[1]
    assert not in_annotation(arg2)
    assert arg2.annotation is not None
    assert in_annotation(arg2.annotation)

    arg3 = func.args.args[2]
    assert not in_annotation(arg3)
    assert isinstance(arg3.annotation, ast.BinOp)
    assert in_annotation(arg3.annotation)
    assert isinstance(arg3.annotation.left, ast.BinOp)
    assert in_annotation(arg3.annotation.left)
    assert in_annotation(arg3.annotation.left.left)
    assert in_annotation(arg3.annotation.left.right)
    assert in_annotation(arg3.annotation.right)

    ret = cast(ast.BinOp, func.returns)
    assert in_annotation(ret)
    assert in_annotation(ret.left)
    assert in_annotation(ret.right)


def test_in_annotation_assign() -> None:
    tree = ast.parse("a: int|None = None")
    set_info_in_tree(tree)

    assert not in_annotation(tree)

    assign: Any = cast(ast.AnnAssign, tree.body[0])
    assert not in_annotation(assign)
    assert in_annotation(assign.annotation)
    assert in_annotation(assign.annotation.left)
    assert in_annotation(assign.annotation.right)


@pytest.mark.skipif(
    sys.version_info < (3, 12), reason="type statement was added in 3.12"
)
def test_is_in_type_statement() -> None:
    tree = ast.parse("type X = int|None")
    set_info_in_tree(tree)
    alias = cast(ast.TypeAlias, tree.body[0])

    assert is_in_type_statement(alias.value)
    assert not is_in_type_statement(alias)
    assert not is_in_type_statement(tree)


def test_is_in_type_statement_unsupported_python_version(mocker: MockerFixture) -> None:
    mocker.patch.object(sys, "version_info", (3, 11))
    tree = ast.parse("a = 1")
    assert not is_in_type_statement(tree)


def test_is_in_type_alias() -> None:
    tree = ast.parse("from typing import TypeAlias; a: TypeAlias = None")
    set_info_in_tree(tree)
    assign = cast(ast.AnnAssign, tree.body[1])

    assert not is_in_type_alias(tree)
    assert not is_in_type_alias(assign)
    assert is_in_type_alias(cast(ast.AST, assign.value))
