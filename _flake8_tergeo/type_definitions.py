"""Type definitions."""

from __future__ import annotations

import ast
from typing import Union

from typing_extensions import ParamSpec, TypeAlias

EllipsisType = type(...)
AnyFunctionDef: TypeAlias = Union[ast.FunctionDef, ast.AsyncFunctionDef]
AnyFor: TypeAlias = Union[ast.For, ast.AsyncFor]
PARAM = ParamSpec("PARAM")
