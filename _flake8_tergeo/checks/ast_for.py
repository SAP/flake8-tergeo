"""For checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register_for
from _flake8_tergeo.type_definitions import AnyFor


@register_for
def check_for(node: AnyFor) -> IssueGenerator:
    """Visit a for node."""
    yield from _check_enumerate(node)


def _check_enumerate(node: AnyFor) -> IssueGenerator:
    # check if the for iter source is enumerate
    if not isinstance(node.iter, ast.Call):
        return
    if not isinstance(node.iter.func, ast.Name):
        return
    if node.iter.func.id != "enumerate":
        return

    # check if the target is a tuple
    if not isinstance(node.target, ast.Tuple):
        return

    if not len(node.target.elts) > 0:
        return

    target = node.target.elts[0]
    if isinstance(target, ast.Name):
        yield from _check_enumerate_target(target)


def _check_enumerate_target(node: ast.Name) -> IssueGenerator:
    if node.id == "_":
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="029",
            message=(
                "If the index variable in an enumerate loop is not needed, "
                "use a classical for loop instead."
            ),
        )
