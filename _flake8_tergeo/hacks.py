"""Hacks to support different python versions."""

from __future__ import annotations

import ast


class _DummyNode(ast.AST):
    pass


def add_python314_removed_ast_nodes() -> None:
    """Add dummy AST nodes for Python 3.14 removed nodes."""
    ast.NameConstant = _DummyNode  # type:ignore[attr-defined]
    ast.Num = _DummyNode  # type:ignore[attr-defined]
    ast.Str = _DummyNode  # type:ignore[attr-defined]
