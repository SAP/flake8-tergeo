"""BinOp checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.ast_util import get_parent, is_constant_node
from _flake8_tergeo.checks.shared import (
    check_annotation_order,
    check_bottom_type_in_union,
)
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register


@register(ast.BinOp)
def check_ast_bin_op(node: ast.BinOp) -> IssueGenerator:
    """Visit a binary operator."""
    yield from _check_percent_format(node)
    yield from _check_annotation_order(node)
    yield from _check_bottom_type_in_union(node)


def _check_percent_format(node: ast.BinOp) -> IssueGenerator:
    if isinstance(node.op, ast.Mod) and (
        is_constant_node(node.left, (str, bytes))
        or isinstance(node.left, ast.JoinedStr)
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="060",
            message="String literal formatting using percent operator.",
        )


def _flatten(node: ast.BinOp) -> list[ast.AST]:
    nodes = []
    if isinstance(node.left, ast.BinOp):
        nodes.extend(_flatten(node.left))
    else:
        nodes.append(node.left)
    nodes.append(node.right)
    return nodes


def _check_annotation_order(node: ast.BinOp) -> IssueGenerator:
    # if the parent is already an BinOp, the parent was checked, so we can return here
    if isinstance(get_parent(node), ast.BinOp):
        return

    annotation_nodes = _flatten(node)
    yield from check_annotation_order(node, annotation_nodes)


def _check_bottom_type_in_union(node: ast.BinOp) -> IssueGenerator:
    yield from check_bottom_type_in_union(node, [node.left, node.right])
