"""Type definitions."""

from __future__ import annotations

import ast
from collections.abc import Generator
from typing import TYPE_CHECKING, Union

from flake8.options.manager import OptionManager as Flake8OptionManager
from typing_extensions import ParamSpec, TypeAlias

if TYPE_CHECKING:
    from _flake8_tergeo.interfaces import Issue

EllipsisType = type(...)
AnyFunctionDef: TypeAlias = Union[ast.FunctionDef, ast.AsyncFunctionDef]
IssueGenerator: TypeAlias = Generator["Issue"]
OptionManager: TypeAlias = Flake8OptionManager
AnyFor: TypeAlias = Union[ast.For, ast.AsyncFor]
PARAM = ParamSpec("PARAM")
