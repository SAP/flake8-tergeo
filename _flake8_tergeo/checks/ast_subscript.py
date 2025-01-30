"""Subscript checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.ast_util import (
    get_subscript_value,
    has_future_annotations,
    in_annotation,
    in_type_checking_block,
    is_constant_node,
    is_expected_node,
    is_float,
)
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.global_options import get_python_version
from _flake8_tergeo.registry import register


@register(ast.Subscript)
def check_subscript(node: ast.Subscript) -> IssueGenerator:
    """Visit a subscript."""
    yield from _check_is_float(node)
    yield from _check_single_item_union(node)
    yield from _check_generator_default(node)


def _check_is_float(node: ast.Subscript) -> IssueGenerator:
    slice_value = get_subscript_value(node)
    if is_float(slice_value):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="048",
            message="Found float used as key.",
        )


def _check_single_item_union(node: ast.Subscript) -> IssueGenerator:
    if not is_expected_node(node.value, "typing", "Union"):
        return
    slice_value = get_subscript_value(node)
    if not isinstance(slice_value, (ast.Name, ast.Attribute, ast.Constant)):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="106",
        message="Found union with only one element.",
    )


def _check_generator_default(node: ast.Subscript) -> IssueGenerator:
    if not (
        get_python_version() >= (3, 13)
        or (has_future_annotations(node) and in_annotation(node))
        or in_type_checking_block(node)
    ):
        return
    if not (
        is_expected_node(node.value, "typing", "Generator")
        or is_expected_node(node.value, "collections.abc", "Generator")
    ):
        return
    slice_value = get_subscript_value(node)
    if not isinstance(slice_value, ast.Tuple):
        return
    if len(slice_value.elts) == 1:
        return
    if not is_constant_node(slice_value.elts[-1], type(None)):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="123",
        message="The 2nd/3rd argument of a Generator annotation can be omitted if they are None.",
    )
