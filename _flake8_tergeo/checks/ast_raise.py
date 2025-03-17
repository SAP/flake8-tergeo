"""Raise checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.ast_util import get_parent, stringify
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register

GENERIC_EXCEPTIONS = ["BaseException", "Exception"]


@register(ast.Raise)
def check_raise(node: ast.Raise) -> IssueGenerator:
    """Check a raise."""
    yield from _check_raise_too_generic(node)
    yield from _check_raise_from_itself(node)
    yield from _check_raise_caught_class(node)


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


def _get_except(node: ast.AST) -> ast.ExceptHandler | None:
    parent: ast.AST | None = node
    while parent:
        if isinstance(parent, ast.ExceptHandler):
            return parent
        parent = get_parent(parent)
    return None


def _get_129_issue(node: ast.Raise) -> Issue:
    return Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="129",
        message="The cause of the raised error is the same as the caught exception.",
    )


def _check_raise_caught_class(node: ast.Raise) -> IssueGenerator:
    if not node.cause or not isinstance(node.cause, (ast.Name, ast.Attribute)):
        return

    except_node = _get_except(node)
    if not except_node:
        return

    cause = stringify(node.cause)

    if isinstance(except_node.type, ast.Tuple):
        for caught in except_node.type.elts:
            if (
                isinstance(caught, (ast.Name, ast.Attribute))
                and stringify(caught) == cause
            ):
                yield _get_129_issue(node)
    elif (
        isinstance(except_node.type, (ast.Name, ast.Attribute))
        and stringify(except_node.type) == cause
    ):
        yield _get_129_issue(node)
