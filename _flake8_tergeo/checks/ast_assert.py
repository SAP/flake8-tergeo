"""Assert checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register


@register(ast.Assert)
def check_assign(node: ast.Assert) -> IssueGenerator:
    """Visit an assign statement."""
    yield from _check_named_expression(node)


def _check_named_expression(node: ast.Assert) -> IssueGenerator:
    for child in ast.walk(node):
        if isinstance(child, ast.NamedExpr):
            yield Issue(
                line=child.lineno,
                column=child.col_offset,
                issue_number="116",
                message="Found named expression (:=) in assert statement.",
            )
