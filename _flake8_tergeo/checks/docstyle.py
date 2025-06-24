# pylint: disable=missing-function-docstring
"""Docstring style checker.

The rules are following the PEP 257 conventions, with some adjustments.
The logic and rules are inspired by ``pydocstyle``.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Union, cast

from typing_extensions import TypeAlias, override

from _flake8_tergeo.ast_util import get_parent, is_expected_node
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.own_base import OwnChecker
from _flake8_tergeo.type_definitions import AnyFunctionDef

DocstringNodes: TypeAlias = Union[
    ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef
]


class DocstyleChecker(OwnChecker):
    """Checker for docstring style according to PEP 257 conventions."""

    def __init__(self, tree: ast.AST, filename: str) -> None:
        super().__init__()
        self._tree = tree
        self._visitor = _Visitor(Path(filename))

    @override
    def check(self) -> IssueGenerator:
        self._visitor.visit(self._tree)
        yield from self._visitor.issues


class _Visitor(ast.NodeVisitor):

    def __init__(self, path: Path) -> None:
        self._path = path
        self.issues: list[Issue] = []

    @override
    def visit_Module(self, node: ast.Module) -> None:
        is_package = self._path.stem == "__init__"
        if is_package and not self._path.parent.stem.startswith("_"):
            self._check_docstring(node, "300", "public package")
        elif not is_package and not self._path.stem.startswith("_"):
            self._check_docstring(node, "307", "public module")
        self.generic_visit(node)

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not self._is_private(node.name):
            self._check_docstring(node, "301", "public class")
        self.generic_visit(node)

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: AnyFunctionDef) -> None:
        if self._is_private(node.name):
            return

        is_override = False
        docstring_node = self._get_docstring(node)
        for decorator in node.decorator_list:
            if is_expected_node(decorator, "typing", "overload") and docstring_node:
                self.issues.append(
                    Issue(
                        line=docstring_node.lineno,
                        column=docstring_node.col_offset,
                        issue_number="312",
                        message="Functions decorated with @overload should not have a docstring.",
                    )
                )
                return
            if is_expected_node(decorator, "typing", "override"):
                is_override = True

        is_within_class = isinstance(get_parent(node), ast.ClassDef)
        if is_within_class and is_override:
            self._check_docstring(node, "306", "overridden method")
            return
        if is_within_class and node.name == "__init__":
            self._check_docstring(node, "305", "__init__")
        elif is_within_class and self._is_magic(node.name):
            self._check_docstring(node, "304", "magic method")
        elif is_within_class:
            self._check_docstring(node, "302", "public method")
        elif self._is_magic(node.name):
            self._check_docstring(node, "313", "magic function")
        else:
            self._check_docstring(node, "303", "public function")

    def _is_private(self, name: str) -> bool:
        return name.startswith("_") and not self._is_magic(name)

    def _is_magic(self, name: str) -> bool:
        return name.startswith("__") and name.endswith("__") and len(name) > 4

    def _get_docstring(self, node: DocstringNodes) -> ast.Constant | None:
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            return None
        value = node.body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value
        return None

    def _check_docstring(
        self,
        node: DocstringNodes,
        missing_issue_number: str,
        type_str: str,
    ) -> None:
        docstring_node = self._get_docstring(node)
        self._check_missing_docstring(
            docstring_node=docstring_node,
            node=node,
            missing_issue_number=missing_issue_number,
            type_str=type_str,
        )

        if not docstring_node:
            return
        self._check_empty_docstring(docstring_node)
        self._check_docstring_format(docstring_node)

    def _check_empty_docstring(self, docstring_node: ast.Constant) -> None:
        docstring = cast(str, docstring_node.value)
        if docstring.strip() == "":
            self.issues.append(
                Issue(
                    line=docstring_node.lineno,
                    column=docstring_node.col_offset,
                    issue_number="308",
                    message="Empty docstring.",
                )
            )

    def _check_docstring_format(self, docstring_node: ast.Constant) -> None:
        lines = cast(str, docstring_node.value).splitlines()
        if not lines:
            return
        for check in (
            self._check_summary_in_first_line,
            self._check_summary_endswith_period,
            self._check_empty_line_after_summary,
        ):
            check(docstring_node, lines)

    def _check_summary_in_first_line(
        self, docstring_node: ast.Constant, lines: list[str]
    ) -> None:
        if lines[0].strip() != "":
            return
        self.issues.append(
            Issue(
                line=docstring_node.lineno,
                column=docstring_node.col_offset,
                issue_number="309",
                message="The summary should be placed in the first line.",
            )
        )

    def _check_summary_endswith_period(
        self, docstring_node: ast.Constant, lines: list[str]
    ) -> None:
        if not lines[0].strip():
            return
        if lines[0].endswith("."):
            return
        self.issues.append(
            Issue(
                line=docstring_node.lineno,
                column=docstring_node.col_offset,
                issue_number="311",
                message="The summary should end with a period.",
            )
        )

    def _check_empty_line_after_summary(
        self, docstring_node: ast.Constant, lines: list[str]
    ) -> None:
        if len(lines) < 2:
            return
        if lines[1].strip() == "":
            return
        self.issues.append(
            Issue(
                line=docstring_node.lineno + 1,
                column=0,
                issue_number="310",
                message="There should be an empty line after the summary.",
            )
        )

    def _check_missing_docstring(
        self,
        node: DocstringNodes,
        docstring_node: ast.Constant | None,
        missing_issue_number: str,
        type_str: str,
    ) -> None:
        if docstring_node is not None:
            return
        self.issues.append(
            Issue(
                line=getattr(node, "lineno", 1),
                column=getattr(node, "col_offset", 0),
                issue_number=missing_issue_number,
                message=f"Missing docstring in {type_str}.",
            )
        )
