"""Lambda checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register


@register(ast.Lambda)
def check_lambda(node: ast.Lambda) -> IssueGenerator:
    """Check a lambda statement."""
    yield from _check_unnecessary_lambda(node)


def _check_unnecessary_lambda(node: ast.Lambda) -> IssueGenerator:
    if node.args.args or node.args.kwarg or node.args.kwonlyargs or node.args.vararg:
        return

    if isinstance(node.body, ast.List) and not node.body.elts:
        yield _create_issue(node, "list")
    if isinstance(node.body, ast.Tuple) and not node.body.elts:
        yield _create_issue(node, "tuple")
    if isinstance(node.body, ast.Dict) and not node.body.keys and not node.body.values:
        yield _create_issue(node, "dict")


def _create_issue(node: ast.Lambda, replacement: str) -> Issue:
    return Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="079",
        message=f"Found lambda statement which can be replaced with {replacement} function.",
    )
