"""Function definition checks."""

from __future__ import annotations

import ast
import re

from _flake8_tergeo.ast_util import get_parent, is_expected_node, is_stub, stringify
from _flake8_tergeo.base import get_plugin
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.registry import register_add_options, register_function_def
from _flake8_tergeo.type_definitions import AnyFunctionDef

PY2_REMOVED_METHODS = [
    "__oct__",
    "__unicode__",
    "__hex__",
    "__coerce__",
    "__nonzero__",
    "__cmp__",
    "__getinitargs__",
    "__delslice__",
    "__setslice__",
    "__getslice__",
]
DESCRIPTORS = ["staticmethod", "property", "classmethod"]
_BOOL_STRING_PATTERN = re.compile("^_*(is|have|has|can)_.*$", re.IGNORECASE)
_GET_STRING_PATTERN = re.compile("^_*get_.*$", re.IGNORECASE)


@register_function_def
def check_func_def(node: AnyFunctionDef) -> IssueGenerator:
    """Check a function definition."""
    yield from _check_assign_and_return(node)
    yield from _check_descriptors(node)
    yield from _check_function_naming(node)
    yield from _check_py2_methods(node)
    yield from _check_class_property(node)
    yield from _check_valid_return_annotation(node)
    yield from _check_override_first_decorator(node)


def _check_assign_and_return(node: AnyFunctionDef) -> IssueGenerator:
    previous_node: ast.AST | None = None
    ignore_ann_assign = get_plugin().get_options().ignore_annotation_in_assign_return
    to_ignore: list[str] = []

    for subnode in ast.walk(node):
        if isinstance(subnode, (ast.Global, ast.Nonlocal)):
            to_ignore.extend(subnode.names)

        if not previous_node:
            previous_node = subnode
            continue

        assign_name = _get_assign_target_id(previous_node, ignore_ann_assign)
        if (
            assign_name
            and isinstance(subnode, ast.Return)
            and isinstance(subnode.value, ast.Name)
            and assign_name == subnode.value.id
            and assign_name not in to_ignore
        ):
            # check if the assign-return is part of a try-block
            try_node = _get_surrounding_try(subnode, node)
            if try_node:
                # get all ast.Name nodes of the finally block of the try
                names = [
                    subnode.id
                    for final_node in try_node.finalbody
                    for subnode in ast.walk(final_node)
                    if isinstance(subnode, ast.Name)
                    and not isinstance(get_parent(subnode), ast.Attribute)
                ]
                if assign_name in names:
                    # if the assign-return name is used in the finally block, don't emit an error
                    continue

            yield Issue(
                line=subnode.lineno,
                column=subnode.col_offset,
                issue_number="071",
                message="Found assign and return. Remove the assignment and return directly.",
            )
        previous_node = subnode


def _get_surrounding_try(node: ast.AST, until: ast.AST) -> ast.Try | None:
    current_node = node
    while current_node is not until:
        if isinstance(current_node, ast.Try):
            return current_node
        parent = get_parent(current_node)
        if not parent:  # pragma: no cover
            return None
        current_node = parent
    return None


def _get_assign_target_id(stmt: ast.AST, ignore_ann_assign: bool) -> str | None:
    if (
        isinstance(stmt, ast.Assign)
        and len(stmt.targets) == 1
        and isinstance(stmt.targets[0], ast.Name)
    ):
        return stmt.targets[0].id
    if (
        not ignore_ann_assign
        and isinstance(stmt, ast.AnnAssign)
        and isinstance(stmt.target, ast.Name)
    ):
        return stmt.target.id
    return None


@register_add_options
def add_options(option_manager: OptionManager) -> None:
    """Add options for this checker."""
    option_manager.add_option(
        "--ignore-annotation-in-assign-return",
        parse_from_config=True,
        action="store_true",
    )


def _has_class_parent(node: ast.AST) -> bool:
    parent = get_parent(node)
    if not parent:  # pragma: no cover
        return False
    if isinstance(parent, ast.ClassDef):
        return True
    if isinstance(parent, ast.If):
        return _has_class_parent(parent)
    return False


def _check_descriptors(node: AnyFunctionDef) -> IssueGenerator:
    for decorator in node.decorator_list:
        if (
            isinstance(decorator, ast.Name)
            and decorator.id in DESCRIPTORS
            and not _has_class_parent(node)
        ):
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="096",
                message=f"Found descriptor {decorator.id} on function outside a class.",
            )


def _check_function_naming(node: AnyFunctionDef) -> IssueGenerator:
    """Check a function definition."""
    yield from _check_boolean(node)
    yield from _check_get(node)


def _is_bool_type(node: ast.expr) -> bool:
    return isinstance(node, ast.Name) and node.id == "bool"


def _is_typeguard(node: ast.expr) -> bool:
    if not isinstance(node, ast.Subscript):
        return False
    return is_expected_node(node.value, "typing", "TypeGuard")


def _is_type_is(node: ast.expr) -> bool:
    if not isinstance(node, ast.Subscript):
        return False
    return is_expected_node(node.value, "typing", "TypeIs")


def _check_boolean(node: AnyFunctionDef) -> IssueGenerator:
    if not _BOOL_STRING_PATTERN.match(node.name):
        return
    if not node.returns:
        return
    if (
        _is_bool_type(node.returns)
        or _is_typeguard(node.returns)
        or _is_type_is(node.returns)
    ):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="093",
        message=(
            f"The function {node.name} implies a boolean return type "
            "but it returns something else."
        ),
    )


def _check_get(node: AnyFunctionDef) -> IssueGenerator:
    if not _GET_STRING_PATTERN.match(node.name):
        return
    if is_stub(node):
        return
    if not any(
        isinstance(child, (ast.Return, ast.Yield, ast.YieldFrom))
        for child in ast.walk(node)
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="043",
            message=(
                f"The function {node.name} implies a return but it returns/yields nothing."
            ),
        )


def _check_py2_methods(node: AnyFunctionDef) -> IssueGenerator:
    """Visit a function definition."""
    if node.name in PY2_REMOVED_METHODS and isinstance(get_parent(node), ast.ClassDef):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="042",
            message=(
                f"The magic method {node.name} is no longer used "
                "in python3 and should be removed."
            ),
        )


def _has_decorator(node: AnyFunctionDef, decorator: str) -> bool:
    return any(
        isinstance(deco, (ast.Name, ast.Attribute)) and stringify(deco) == decorator
        for deco in node.decorator_list
    )


def _check_class_property(node: AnyFunctionDef) -> IssueGenerator:
    """Check a function definition."""
    if _has_decorator(node, "property") and _has_decorator(node, "classmethod"):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="122",
            message="The behavior of a classmethod and property decorator is unreliable. "
            "Avoid defining class properties.",
        )


def _check_valid_return_annotation(node: AnyFunctionDef) -> IssueGenerator:
    if not node.returns:
        return
    for child in ast.walk(node.returns):
        if not is_expected_node(child, "typing", "Never"):
            continue
        yield Issue(
            line=child.lineno,
            column=child.col_offset,
            issue_number="107",
            message="Instead of using typing.Never for return annotations, use typing.NoReturn.",
        )


def _check_override_first_decorator(node: AnyFunctionDef) -> IssueGenerator:
    decorator_list = node.decorator_list
    if not decorator_list or len(decorator_list) == 1:
        return

    for index, decorator in enumerate(decorator_list):
        if not is_expected_node(decorator, "typing", "override"):
            continue

        try:
            descriptor_index: int | None = next(
                idx
                for idx, val in enumerate(decorator_list)
                if isinstance(val, ast.Name) and val.id in DESCRIPTORS
            )
        except StopIteration:
            descriptor_index = None

        if descriptor_index is None and index == 0:
            return
        if descriptor_index is not None and index == descriptor_index + 1:
            return

        yield Issue(
            line=decorator.lineno,
            column=decorator.col_offset,
            issue_number="125",
            message="The override decorator should be the first decorator or "
            "if present placed directly below descriptor based decorators.",
        )
