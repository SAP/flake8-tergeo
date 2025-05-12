"""Shared checks for flake8-tergeo."""

from __future__ import annotations

import ast
from collections.abc import Collection

from _flake8_tergeo.ast_util import (
    in_annotation,
    is_constant_node,
    is_expected_node,
    is_in_type_alias,
    is_in_type_statement,
)
from _flake8_tergeo.flake8_types import Issue, IssueGenerator

BOTTOM_TYPES = ["Never", "NoReturn"]


def check_annotation_order(
    node: ast.expr, nodes: Collection[ast.AST]
) -> IssueGenerator:
    """Check the order of annotations."""
    # if we don't check something for typing, we can skip the check
    if (
        not in_annotation(node)
        and not is_in_type_alias(node)
        and not is_in_type_statement(node)
    ):
        return

    for index, annotation_node in enumerate(nodes):
        # not a None
        if not is_constant_node(annotation_node, type(None)):
            continue
        # we are at the end, so the None is fine at this position
        if index + 1 == len(nodes):
            continue
        yield Issue(
            line=annotation_node.lineno,
            column=annotation_node.col_offset,
            issue_number="077",
            message="None should be the last value in an annotation.",
        )


def check_bottom_type_in_union(
    node: ast.expr, nodes: Collection[ast.AST]
) -> IssueGenerator:
    """Check for bottom types in unions."""
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
        for subnode in nodes
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="104",
            message="Bottom types (Never/NoReturn) should not be used in unions.",
        )
