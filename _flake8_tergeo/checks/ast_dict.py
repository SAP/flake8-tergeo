"""Dict checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.ast_util import is_float
from _flake8_tergeo.interfaces import Issue
from _flake8_tergeo.registry import register
from _flake8_tergeo.type_definitions import IssueGenerator


@register(ast.Dict)
def check_dict(node: ast.Dict) -> IssueGenerator:
    """Visit a dict."""
    yield from _check_is_float(node)
    yield from _check_unpack(node)
    yield from _check_union(node)


def _check_is_float(node: ast.Dict) -> IssueGenerator:
    for key in node.keys:
        if is_float(key):
            yield Issue(
                line=key.lineno,
                column=key.col_offset,
                issue_number="048",
                message="Found float used as key.",
            )


def _check_unpack(node: ast.Dict) -> IssueGenerator:
    for index, key in enumerate(node.keys):
        if not key and isinstance(node.values[index], ast.Dict):
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="095",
                message="Instead of declaring a dictionary and directly unpacking it, "
                "specify the keys and values in the outer dictionary.",
            )


def _check_union(node: ast.Dict) -> IssueGenerator:
    if not node.keys:
        return

    if node.keys[0] is None or node.keys[-1] is None:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="101",
            message="Instead of using the unpack operator for the first/last element in a dict, "
            "use the union operator ('|') instead",
        )
