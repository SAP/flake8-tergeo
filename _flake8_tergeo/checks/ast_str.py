"""Str checks."""

from __future__ import annotations

import ast
import string

from _flake8_tergeo.ast_util import is_constant_node
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register


@register(ast.Constant)
def check_constant_string(node: ast.Constant) -> IssueGenerator:
    """Check a constant which represents a string."""
    if is_constant_node(node, str):
        yield from _check_alphabet(node)


def _check_alphabet(node: ast.Constant) -> IssueGenerator:
    issues = list(_compare(node, string.ascii_letters, "021", "string.ascii_letters"))
    if issues:
        yield from issues
    else:
        yield from _compare(
            node, string.ascii_lowercase, "022", "string.ascii_lowercase"
        )
        yield from _compare(
            node, string.ascii_uppercase, "023", "string.ascii_uppercase"
        )
    yield from _compare(node, string.digits, "024", "string.digits")


def _compare(
    value: ast.Constant, compare: str, issue_number: str, compare_name: str
) -> IssueGenerator:
    if compare in value.value:
        yield Issue(
            line=value.lineno,
            column=value.col_offset,
            issue_number=issue_number,
            message=f"Found string value which can be replaced with {compare_name}",
        )
