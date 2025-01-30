"""Exception Handler checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register


@register(ast.ExceptHandler)
def check_except_handler(node: ast.ExceptHandler) -> IssueGenerator:
    """Check an except handler."""
    yield from _check_except_with_reraise(node)


def _check_except_with_reraise(node: ast.ExceptHandler) -> IssueGenerator:
    if len(node.body) != 1 or not node.name:
        return

    body = node.body[0]
    if (
        not isinstance(body, ast.Raise)
        or body.cause
        or not body.exc
        or not isinstance(body.exc, ast.Name)
    ):
        return
    if node.name == body.exc.id:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="046",
            message="Catching an exception with a direct reraise can be removed.",
        )
