"""Raise checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.ast_util import stringify
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register

GENERIC_EXCEPTIONS = ["BaseException", "Exception"]


@register(ast.Raise)
def check_raise(node: ast.Raise) -> IssueGenerator:
    """Check a raise."""
    yield from _check_raise_too_generic(node)
    yield from _check_raise_from_itself(node)


def _check_raise_too_generic(node: ast.Raise) -> IssueGenerator:
    if isinstance(node.exc, ast.Name):
        name = node.exc.id
    elif isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
        name = node.exc.func.id
    else:
        return

    if name in GENERIC_EXCEPTIONS:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="047",
            message=(
                f"Raising {name} is too generic "
                "and should be replaced with a more concrete subclass."
            ),
        )


def _check_raise_from_itself(node: ast.Raise) -> IssueGenerator:
    if not node.cause or not isinstance(node.cause, (ast.Name, ast.Attribute)):
        return
    if not node.exc or not isinstance(node.exc, (ast.Name, ast.Attribute)):
        return
    if stringify(node.exc) == stringify(node.cause):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="044",
            message="Found exception raised from itself.",
        )
