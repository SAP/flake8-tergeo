"""Name/Attribute checks."""

from __future__ import annotations

import ast
from typing import Union

from typing_extensions import TypeAlias

from _flake8_tergeo.ast_util import (
    get_parent,
    has_future_annotations,
    in_annotation,
    in_args_assign_annotation,
    in_type_checking_block,
    is_expected_node,
    stringify,
)
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.global_options import get_python_version
from _flake8_tergeo.registry import register

NameOrAttribute: TypeAlias = Union[ast.Name, ast.Attribute]
OS_ALIASES = ["EnvironmentError", "IOError", "WindowsError"]
BUILTINS = ["Tuple", "List", "Dict", "Set", "FrozenSet", "Type"]
OS_DEPENDENT_PATH = ["PurePosixPath", "PureWindowsPath", "PosixPath", "WindowsPath"]


@register(ast.Name)
def check_name(node: ast.Name) -> IssueGenerator:
    """Check a name."""
    yield from _check_debug_constant(node)
    yield from _check_builtin_os_alias(node)
    yield from _check_metaclass_constant(node)
    yield from _check_dunder_in_name(node)


@register(ast.Name, ast.Attribute)
def check_name_or_attribute(node: NameOrAttribute) -> IssueGenerator:
    """Check a name or attribute."""
    yield from _check_new_union_syntax(node)
    yield from _check_generic_builtins(node)
    yield from _check_optional_new_union_syntax(node)
    yield from _check_utc_constant(node)
    yield from _check_regex_debug(node)
    yield from _check_requests_codes(node)
    yield from _check_os_dependent_path(node)
    yield from _check_nested_union(node)
    yield from _check_valid_arg_assign_annotation(node)
    yield from _check_datetime_utcnow(node)
    yield from _check_datetime_utcfromtimestamp(node)


def _check_builtin_os_alias(node: ast.Name) -> IssueGenerator:
    if node.id in OS_ALIASES:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="089",
            message=f"Found OSError alias {node.id}; use OSError instead.",
        )


def _check_debug_constant(node: ast.Name) -> IssueGenerator:
    if node.id == "__debug__":
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="064",
            message="Found use of __debug__.",
        )


def _check_dunder_in_name(node: ast.Name) -> IssueGenerator:
    if "__" in node.id[1:-1]:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="039",
            message="Found dunder in the middle of a name.",
        )


def _check_metaclass_constant(node: ast.Name) -> IssueGenerator:
    if node.id == "__metaclass__":
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="016",
            message="Found use of __metaclass__. Use metaclass= in the class signature",
        )


def _check_regex_debug(node: NameOrAttribute) -> IssueGenerator:
    if not is_expected_node(node, "re", "DEBUG"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="076",
        message="Found usage/import of re.DEBUG.",
    )


def _supports_new_union_syntax() -> bool:
    return get_python_version() >= (3, 10)


def _supports_generics_in_stdlib() -> bool:
    return get_python_version() >= (3, 9)


def _use_new_union_syntax(node: NameOrAttribute, typing_node: str) -> bool:
    if not (
        _supports_new_union_syntax()
        or (has_future_annotations(node) and in_annotation(node))
        or in_type_checking_block(node)
    ):
        return False
    return is_expected_node(node, "typing", typing_node)


def _check_new_union_syntax(node: NameOrAttribute) -> IssueGenerator:
    if not _use_new_union_syntax(node, "Union"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="054",
        message="Use PEP 604 syntax for unions.",
    )


def _check_optional_new_union_syntax(node: NameOrAttribute) -> IssueGenerator:
    if not _use_new_union_syntax(node, "Optional"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="055",
        message="Use PEP 604 syntax for Optional[X] like 'X|None'.",
    )


def _check_generic_builtins(node: NameOrAttribute) -> IssueGenerator:
    if not (
        _supports_generics_in_stdlib()
        or (has_future_annotations(node) and in_annotation(node))
        or in_type_checking_block(node)
    ):
        return

    simple_name = stringify(node).rsplit(".", maxsplit=1)[-1]
    if simple_name not in BUILTINS:
        return
    if not is_expected_node(node, "typing", simple_name):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="056",
        message=f"Use builtin {simple_name.lower()} instead of {simple_name}.",
    )


def _check_utc_constant(node: NameOrAttribute) -> IssueGenerator:
    if get_python_version() < (3, 11):
        return
    if not is_expected_node(node, "datetime", "timezone.utc"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="099",
        message="Use datetime.UTC instead of datetime.timezone.utc.",
    )


def _check_requests_codes(node: NameOrAttribute) -> IssueGenerator:
    if not (
        is_expected_node(node, "requests", "codes")
        or is_expected_node(node, "requests.status_codes", "codes")
    ):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="220",
        message="Use http.HTTPStatus instead of requests.codes.",
    )


def _check_os_dependent_path(node: NameOrAttribute) -> IssueGenerator:
    if not any(is_expected_node(node, "pathlib", name) for name in OS_DEPENDENT_PATH):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="103",
        message="Use the OS independent classes pathlib.Path or pathlib.PurePath instead of OS "
        "dependent ones.",
    )


def _check_nested_union(node: NameOrAttribute) -> IssueGenerator:
    if not is_expected_node(node, "typing", "Union"):
        return

    # 1. Union[X, Union[X, Y]]
    # -> ast.Subscript -> ast.Tuple -> ast.Subscript
    # 2. Union[Union[Y, X]]
    # -> ast.Subscript -> ast.Subscript

    # check if Union is used as a subscript
    parent = get_parent(node)
    if not isinstance(parent, ast.Subscript):
        return

    parent = get_parent(parent)
    # if the parent is a tuple (first case), we need to go one level up
    if isinstance(parent, ast.Tuple):
        parent = get_parent(parent)
    # check if now the parent is a subscript ...
    if not isinstance(parent, ast.Subscript):
        return
    # ... and the value of the subscript is an union
    if not is_expected_node(parent.value, "typing", "Union"):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="105",
        message="Found nested union. Use a single Union instead.",
    )


def _check_valid_arg_assign_annotation(node: NameOrAttribute) -> IssueGenerator:
    if not in_args_assign_annotation(node):
        return
    if not is_expected_node(node, "typing", "NoReturn"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="108",
        message="Instead of using typing.NoReturn for annotations, use typing.Never.",
    )


def _check_datetime_utcnow(node: NameOrAttribute) -> IssueGenerator:
    if not is_expected_node(node, "datetime.datetime", "utcnow"):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="003",
        message=(
            "Found usage/import of datetime.utcnow. "
            "Consider to use datetime.now(tz=)."
        ),
    )


def _check_datetime_utcfromtimestamp(node: NameOrAttribute) -> IssueGenerator:
    if not is_expected_node(node, "datetime.datetime", "utcfromtimestamp"):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="007",
        message=(
            "Found usage/import of datetime.utcfromtimestamp. "
            "Consider to use datetime.fromtimestamp(tz=)."
        ),
    )
