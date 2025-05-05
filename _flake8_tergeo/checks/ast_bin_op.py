"""BinOp checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.ast_util import (
    get_parent,
    in_annotation,
    is_constant_node,
    is_expected_node,
    is_in_type_alias,
    is_in_type_statement,
)
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register

BOTTOM_TYPES = ["Never", "NoReturn"]


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
    # if we don't check something for typing, we can skip the check
    if (
        not in_annotation(node)
        and not is_in_type_alias(node)
        and not is_in_type_statement(node)
    ):
        return
    # if the parent is already an BinOp, the parent was checked, so we can return here
    if isinstance(get_parent(node), ast.BinOp):
        return

    annotation_nodes = _flatten(node)
    for index, annotation_node in enumerate(annotation_nodes):
        # not a None
        if not is_constant_node(annotation_node, type(None)):
            continue
        # we are at the end, so the None is fine at this position
        if index + 1 == len(annotation_nodes):
            continue
        yield Issue(
            line=annotation_node.lineno,
            column=annotation_node.col_offset,
            issue_number="077",
            message="None should be the last value in an annotation.",
        )


def _check_bottom_type_in_union(node: ast.BinOp) -> IssueGenerator:
    # if we don't check something for typing, we can skip the check
    if (
        not in_annotation(node)
        and not is_in_type_alias(node)
        and not is_in_type_statement(node)
    ):
        return

    if any(
        is_expected_node(subnode, "typing", name)
        for name in BOTTOM_TYPES
        for subnode in (node.left, node.right)
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="104",
            message="Bottom types (Never/NoReturn) should not be used in unions.",
        )
