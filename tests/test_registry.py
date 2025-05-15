"""Tests for _flake8_tergeo.registry."""

from __future__ import annotations

import ast
from collections.abc import Callable
from typing import Any

import pytest
from pytest_mock import MockerFixture

from _flake8_tergeo import registry


def test_register(mocker: MockerFixture) -> None:
    mocker.patch.dict(registry.AST_REGISTRY, clear=True)

    func_call1 = mocker.Mock()
    func_call_or_name = mocker.Mock()
    func_delete = mocker.Mock()

    registry.register(ast.Call)(func_call1)
    registry.register(ast.Call, ast.Name)(func_call_or_name)
    registry.register(ast.Delete)(func_delete)

    assert registry.AST_REGISTRY == {
        ast.Call: [func_call1, func_call_or_name],
        ast.Delete: [func_delete],
        ast.Name: [func_call_or_name],
    }


def test_register_function_def(mocker: MockerFixture) -> None:
    mocker.patch.dict(registry.AST_REGISTRY, clear=True)

    func1 = mocker.Mock()
    func2 = mocker.Mock()

    registry.register_function_def(func1)
    registry.register_function_def(func2)

    assert registry.AST_REGISTRY == {
        ast.FunctionDef: [func1, func2],
        ast.AsyncFunctionDef: [func1, func2],
    }


def test_register_for(mocker: MockerFixture) -> None:
    mocker.patch.dict(registry.AST_REGISTRY, clear=True)

    func1 = mocker.Mock()
    func2 = mocker.Mock()

    registry.register_for(func1)
    registry.register_for(func2)

    assert registry.AST_REGISTRY == {
        ast.For: [func1, func2],
        ast.AsyncFor: [func1, func2],
    }


@pytest.mark.parametrize(
    "constant,func",
    [
        ("TOKEN_REGISTRY", registry.register_token_checker),
        ("ADD_OPTIONS_REGISTRY", registry.register_add_options),
        ("PARSE_OPTIONS_REGISTRY", registry.register_parse_options),
    ],
)
def test_simple_register_functions(
    mocker: MockerFixture, constant: str, func: Callable[..., Any]
) -> None:
    mocker.patch.object(registry, constant, [])

    func1 = mocker.Mock()
    func2 = mocker.Mock()

    func(func1)
    func(func2)
    assert getattr(registry, constant) == [func1, func2]
