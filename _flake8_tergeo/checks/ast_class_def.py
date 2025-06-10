"""Class definition checks."""

from __future__ import annotations

import ast

from _flake8_tergeo.ast_util import is_expected_node, stringify
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.global_options import get_python_version
from _flake8_tergeo.registry import register
from _flake8_tergeo.type_definitions import AnyFunctionDef

CACHE_DECORATOR_FACTORIES = [
    ("functools", "lru_cache"),
]
CACHE_DECORATORS = [
    ("functools", "cache"),
] + CACHE_DECORATOR_FACTORIES
ENUM_CLASSES = ("Enum", "IntEnum", "StrEnum")


@register(ast.ClassDef)
def check_ast_class_def(node: ast.ClassDef) -> IssueGenerator:
    """Check a class definition."""
    yield from _check_abc(node)
    yield from _check_extend_base_exception(node)
    yield from _check_enum_has_unique_decorator(node)
    yield from _check_lru_on_class(node)
    yield from _check_enum_bases(node)
    yield from _check_duplicate_class_fields(node)
    yield from _check_class_extends_generic(node)


def _check_abc(node: ast.ClassDef) -> IssueGenerator:
    for keyword in node.keywords:
        if keyword.arg == "metaclass" and is_expected_node(
            keyword.value, "abc", "ABCMeta"
        ):
            code = f"{node.name}(abc.ABC)"
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="082",
                message=f"Unnecessary use of abstract metaclass. Use {code} instead.",
            )


def _check_extend_base_exception(node: ast.ClassDef) -> IssueGenerator:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "BaseException":
            yield Issue(
                line=base.lineno,
                column=base.col_offset,
                issue_number="009",
                message="Found class extending BaseException. Use Exception instead.",
            )


def _check_enum_has_unique_decorator(node: ast.ClassDef) -> IssueGenerator:
    if not any(
        base
        for cls in ENUM_CLASSES
        for base in node.bases
        if is_expected_node(base, "enum", cls)
    ) or any(
        decorator
        for decorator in node.decorator_list
        if is_expected_node(decorator, "enum", "unique")
    ):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="097",
        message=f"Enum '{node.name}' is missing the unique decorator.",
    )


def _check_lru_on_class(node: ast.ClassDef) -> IssueGenerator:
    for child in ast.walk(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield from _check_function_definition(child)


def _check_function_definition(node: AnyFunctionDef) -> IssueGenerator:
    for decorator in node.decorator_list:
        if isinstance(decorator, (ast.Name, ast.Attribute)):
            decorator_name = stringify(decorator)
            if decorator_name in {"staticmethod", "classmethod"}:
                return
            if not any(
                is_expected_node(decorator, module, attr)
                for module, attr in CACHE_DECORATORS
            ):
                continue
            yield _create_074_issue(decorator)
        # currently, there are no other things than names, attributes and calls which can be
        # a decorator, but maybe this changes in the future
        elif isinstance(decorator, ast.Call):  # pragma: no branch
            if not any(
                is_expected_node(decorator.func, module, attr)
                for module, attr in CACHE_DECORATOR_FACTORIES
            ):
                continue
            yield _create_074_issue(decorator)


def _create_074_issue(node: ast.Name | ast.Attribute | ast.Call) -> Issue:
    return Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="074",
        message="Using a cache function on a method can lead to memory leaks.",
    )


def _check_enum_bases(node: ast.ClassDef) -> IssueGenerator:
    if not any(base for base in node.bases if is_expected_node(base, "enum", "Enum")):
        return

    bases = [stringify(base) for base in node.bases if isinstance(base, ast.Name)]
    if "int" in bases:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="066",
            message="Instead of extending both Enum and int, use enum.IntEnum instead.",
        )
    elif "str" in bases and get_python_version() >= (3, 11):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="067",
            message="Instead of extending both Enum and str, use enum.StrEnum instead.",
        )


def _check_duplicate_class_fields(node: ast.ClassDef) -> IssueGenerator:
    seen: set[str] = set()
    for child in node.body:
        if not isinstance(child, ast.Assign):
            continue
        for target_node in child.targets:
            if not isinstance(target_node, ast.Name):
                continue
            target = stringify(target_node)
            if target in seen:
                yield Issue(
                    line=child.lineno,
                    column=child.col_offset,
                    issue_number="005",
                    message=(
                        f"Found duplicated class field {target}. "
                        "If a calculation is needed, refactor the code out to a function "
                        "and use only one assign statement."
                    ),
                )
            seen.add(target)


def _check_class_extends_generic(node: ast.ClassDef) -> IssueGenerator:
    if get_python_version() < (3, 12):
        return
    for base in node.bases:
        if isinstance(base, ast.Subscript) and is_expected_node(
            base.value, "typing", "Generic"
        ):
            yield Issue(
                line=base.lineno,
                column=base.col_offset,
                issue_number="128",
                message="Use the new generic syntax instead of Generic.",
            )
