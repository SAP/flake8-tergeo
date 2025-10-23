"""Type definitions."""

from __future__ import annotations

import ast
from collections.abc import Generator
from typing import TYPE_CHECKING, TypeAlias, Union

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from _flake8_tergeo.interfaces import Issue

EllipsisType = type(...)
AnyFunctionDef: TypeAlias = Union[ast.FunctionDef, ast.AsyncFunctionDef]
IssueGenerator: TypeAlias = Generator["Issue"]
AnyFor: TypeAlias = Union[ast.For, ast.AsyncFor]
PARAM = ParamSpec("PARAM")
