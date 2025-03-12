"""Assign checks."""

from __future__ import annotations

import ast
from dataclasses import dataclass

from _flake8_tergeo.ast_util import (
    get_parent,
    get_parents,
    is_constant_node,
    is_expected_node,
)
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.global_options import get_python_version
from _flake8_tergeo.registry import register

BAD_NAMES = ["pi", "e", "tau", "inf", "nan"]


@dataclass
class Assignment:
    """Abstract representation of an assignment."""

    target: ast.expr
    lineno: int
    col_offset: int
    value: ast.expr | None
    node: ast.Assign | ast.AnnAssign

    @staticmethod
    def create(node: ast.Assign | ast.AnnAssign) -> list[Assignment]:
        """Create an assignment from an ast node."""
        if isinstance(node, ast.Assign):
            return [
                Assignment(
                    target=target,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    value=node.value,
                    node=node,
                )
                for target in node.targets
            ]
        return [
            Assignment(
                target=node.target,
                lineno=node.lineno,
                col_offset=node.col_offset,
                value=node.value,
                node=node,
            )
        ]


@register(ast.Assign, ast.AnnAssign)
def check_assign(node: ast.Assign | ast.AnnAssign) -> IssueGenerator:
    """Visit an assign statement."""
    for assignment in Assignment.create(node):
        yield from _check_sorted_assigns(assignment)
        yield from _check_single_element_unpacking(assignment)
        yield from _check_bad_name(assignment)
        yield from _check_invalid_slots_type(assignment)
        yield from _check_slots_assign(assignment)
        yield from _check_all_only_on_module(assignment)
        yield from _check_type_alias(assignment)


def _check_all_only_on_module(assignment: Assignment) -> IssueGenerator:
    if not isinstance(assignment.target, ast.Name):
        return
    if assignment.target.id != "__all__":
        return

    parent = get_parent(assignment.node)
    if not isinstance(parent, ast.Module):
        yield Issue(
            line=assignment.lineno,
            column=assignment.col_offset,
            issue_number="124",
            message="__all__ should only be assigned on module level",
        )


def _check_sorted_assigns(assignment: Assignment) -> IssueGenerator:
    if not isinstance(assignment.target, ast.Name):
        return
    if not assignment.value:
        return

    if assignment.target.id == "__all__":
        yield from _check_sorted(
            assignment,
            assignment.value,
            issue_number="090",
            message="Found unsorted __all__.",
        )
    elif assignment.target.id == "__slots__":
        yield from _check_sorted(
            assignment,
            assignment.value,
            issue_number="119",
            message="Found unsorted __slots__.",
        )


def _check_sorted(
    assignment: Assignment, value: ast.expr, issue_number: str, message: str
) -> IssueGenerator:
    if not isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        return

    elements = [
        element.value for element in value.elts if is_constant_node(element, str)
    ]
    if sorted(elements) != elements:
        yield Issue(
            line=assignment.lineno,
            column=assignment.col_offset,
            issue_number=issue_number,
            message=message,
        )


def _check_single_element_unpacking(assignment: Assignment) -> IssueGenerator:
    if not assignment.value:
        return
    if not isinstance(assignment.target, (ast.Tuple, ast.List)):
        return
    if len(assignment.target.elts) != 1:
        return
    yield Issue(
        line=assignment.lineno,
        column=assignment.col_offset,
        issue_number="049",
        message="Found single element unpacking.",
    )


def _check_bad_name(assignment: Assignment) -> IssueGenerator:
    target = assignment.target
    if isinstance(target, ast.Name) and target.id in BAD_NAMES:
        yield Issue(
            line=assignment.lineno,
            column=assignment.col_offset,
            issue_number="069",
            message=f"Using a variable named {target.id} can lead to confusion. "
            "Consider using another name.",
        )


def _check_invalid_slots_type(assignment: Assignment) -> IssueGenerator:
    if not _has_slots_target(assignment):
        return
    if not assignment.value:
        return
    if not isinstance(assignment.value, (ast.Tuple, ast.Dict)):
        yield Issue(
            line=assignment.lineno,
            column=assignment.col_offset,
            issue_number="094",
            message="__slots__ should be defined as a tuple or dict.",
        )


def _check_slots_assign(assignment: Assignment) -> IssueGenerator:
    if not _has_slots_target(assignment):
        return
    for parent in get_parents(assignment.node):
        if isinstance(parent, ast.ClassDef):
            # the first container parent we found is a class -> fine; we can stop
            break
        if isinstance(
            parent,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module),
        ):
            # the first container parent is not a class -> yield and stop
            yield Issue(
                line=assignment.lineno,
                column=assignment.col_offset,
                issue_number="120",
                message="Found __slots__ assignment outside of a class.",
            )
            break
    else:  # pragma: no cover
        # this branch is not reachable since the top-level container is always a module
        return  # noop code for coverage exclusion


def _has_slots_target(assignment: Assignment) -> bool:
    return (
        isinstance(assignment.target, ast.Name) and assignment.target.id == "__slots__"
    )


def _check_type_alias(assignment: Assignment) -> IssueGenerator:
    if get_python_version() < (3, 12):
        return
    if not isinstance(assignment.node, ast.AnnAssign):
        return
    if not is_expected_node(assignment.node.annotation, "typing", "TypeAlias"):
        return
    yield Issue(
        line=assignment.lineno,
        column=assignment.col_offset,
        issue_number="126",
        message="TypeAlias is deprecated and the type statements should be used instead.",
    )
