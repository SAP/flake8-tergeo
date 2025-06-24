"""Registry for AST checkers."""

from __future__ import annotations

import ast
import collections
import tokenize
from argparse import Namespace
from collections.abc import Callable, Sequence
from typing import Any

from typing_extensions import TypeAlias

from _flake8_tergeo.flake8_types import IssueGenerator, OptionManager
from _flake8_tergeo.type_definitions import PARAM, AnyFor, AnyFunctionDef

TokenFunc: TypeAlias = Callable[[Sequence[tokenize.TokenInfo]], IssueGenerator]
AddOptionsFunc: TypeAlias = Callable[[OptionManager], None]
ParseOptionsFunc: TypeAlias = Callable[[Namespace], None]

AST_REGISTRY: dict[type[ast.AST], list[Callable[[Any], IssueGenerator]]] = (
    collections.defaultdict(list)
)
TOKEN_REGISTRY: list[TokenFunc] = []
ADD_OPTIONS_REGISTRY: list[AddOptionsFunc] = []
PARSE_OPTIONS_REGISTRY: list[ParseOptionsFunc] = []


def register_function_def(
    func: Callable[[AnyFunctionDef], IssueGenerator],
) -> Callable[[AnyFunctionDef], IssueGenerator]:
    """Register a AST visit method for function definitions.

    This includes :py:class:`ast.FunctionDef` and :py:class:`ast.AsyncFunctionDef`.
    """
    AST_REGISTRY[ast.FunctionDef].append(func)
    AST_REGISTRY[ast.AsyncFunctionDef].append(func)
    return func


def register_for(
    func: Callable[[AnyFor], IssueGenerator],
) -> Callable[[AnyFor], IssueGenerator]:
    """Register a AST visit method for for loops.

    This includes :py:class:`ast.For` and :py:class:`ast.AsyncFor`.
    """
    AST_REGISTRY[ast.For].append(func)
    AST_REGISTRY[ast.AsyncFor].append(func)
    return func


def register(
    *type_: type[ast.AST],
) -> Callable[[Callable[PARAM, IssueGenerator]], Callable[PARAM, IssueGenerator]]:
    """Decorator to register a AST visit method."""

    def _register_decorator(
        func: Callable[PARAM, IssueGenerator],
    ) -> Callable[PARAM, IssueGenerator]:
        for ast_type in type_:
            AST_REGISTRY[ast_type].append(func)
        return func

    return _register_decorator


def register_token_checker(func: TokenFunc) -> TokenFunc:
    """Decorator to a register a token checker method."""
    TOKEN_REGISTRY.append(func)
    return func


def register_add_options(func: AddOptionsFunc) -> AddOptionsFunc:
    """Register a function which adds flake8 options."""
    ADD_OPTIONS_REGISTRY.append(func)
    return func


def register_parse_options(func: ParseOptionsFunc) -> ParseOptionsFunc:
    """Register a function which parses options."""
    PARSE_OPTIONS_REGISTRY.append(func)
    return func
