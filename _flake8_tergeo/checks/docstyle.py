# pylint: disable=missing-function-docstring
"""Docstring style checker.

The rules are following the PEP 257 conventions, with some adjustments.
The logic and rules are inspired by ``pydocstyle``.

We won't implement the following rules as they are covered by black:

* empty string before docstring
* docstring starts or ends with spaces
* usage of '''
"""

from __future__ import annotations

import ast
import tokenize
from argparse import Namespace
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, Union, cast

from typing_extensions import TypeAlias, override

from _flake8_tergeo import base
from _flake8_tergeo.ast_util import get_parent, is_expected_node
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.own_base import OwnChecker
from _flake8_tergeo.registry import register_add_options, register_parse_options
from _flake8_tergeo.type_definitions import AnyFunctionDef

DocstringNodes: TypeAlias = Union[
    ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef
]


class _ParseOptions(Protocol):
    docstyle_lowercase_words: list[str]


class DocstyleChecker(OwnChecker):
    """Checker for docstring style according to PEP 257 conventions."""

    def __init__(
        self, tree: ast.AST, filename: str, file_tokens: Sequence[tokenize.TokenInfo]
    ) -> None:
        super().__init__()
        self._tree = tree
        self._visitor = _Visitor(Path(filename), file_tokens)

    @override
    def check(self) -> IssueGenerator:
        self._visitor.visit(self._tree)
        yield from self._visitor.issues


class _Visitor(ast.NodeVisitor):

    def __init__(self, path: Path, file_tokens: Sequence[tokenize.TokenInfo]) -> None:
        self._path = path
        self._file_tokens = file_tokens
        self.issues: list[Issue] = []
        self._options: _ParseOptions = base.get_plugin().get_options()

    @override
    def visit_Module(self, node: ast.Module) -> None:
        is_package = self._path.stem == "__init__"
        if is_package:
            is_private = self._path.parent.stem.startswith("_")
            self._check_docstring(node, "300", "public package", is_private=is_private)
        elif not is_package:
            is_private = self._path.stem.startswith("_")
            self._check_docstring(node, "307", "public module", is_private=is_private)
        self.generic_visit(node)

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check_docstring(
            node, "301", "public class", is_private=self._is_private(node.name)
        )
        self.generic_visit(node)

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: AnyFunctionDef) -> None:  # noqa: C901
        is_override = False
        is_private = self._is_private(node.name)
        docstring_node = self._get_docstring(node)

        for decorator in node.decorator_list:
            if is_expected_node(decorator, "typing", "overload"):
                if docstring_node:
                    self.issues.append(
                        Issue(
                            line=docstring_node.lineno,
                            column=docstring_node.col_offset,
                            issue_number="312",
                            message=(
                                "Functions decorated with @overload should not have a docstring."
                            ),
                        )
                    )
                # overloaded functions should not have a docstring and are not further checked
                return
            if is_expected_node(decorator, "typing", "override"):
                is_override = True

        is_within_class = isinstance(get_parent(node), ast.ClassDef)
        if is_within_class and is_override:
            self._check_docstring(
                node, "306", "overridden method", is_private=is_private
            )
            return
        if is_within_class and node.name == "__init__":
            self._check_docstring(node, "305", "__init__", is_private=is_private)
        elif is_within_class and self._is_magic(node.name):
            self._check_docstring(node, "304", "magic method", is_private=is_private)
        elif is_within_class:
            self._check_docstring(node, "302", "public method", is_private=is_private)
        elif self._is_magic(node.name):
            self._check_docstring(node, "313", "magic function", is_private=is_private)
        else:
            self._check_docstring(node, "303", "public function", is_private=is_private)

        if docstring_node:
            self._check_no_empty_line_after_docstring(node, docstring_node)
            self._check_right_quotes(docstring_node)

    def _check_no_empty_line_after_docstring(
        self, node: AnyFunctionDef, docstring_node: ast.Constant
    ) -> None:
        if len(node.body) == 1:
            # the function only has a docstring, so nothing more to check
            return
        if isinstance(
            node.body[1], (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            # if the next node is a function or class, there should be a newline, but its up
            # to the user or formatter to decide that
            return
        if docstring_node.end_lineno is None:
            # this can happen for non cpython based parsers
            return

        token_after_docstring = next(
            (
                token
                for token in self._file_tokens
                if token.start[0] == docstring_node.end_lineno + 1
            ),
            None,
        )
        if not token_after_docstring:
            return
        if token_after_docstring.type != tokenize.NL:
            return

        self.issues.append(
            Issue(
                line=token_after_docstring.start[0],
                column=token_after_docstring.start[1],
                issue_number="314",
                message="A function/method docstring should not be followed by a newline.",
            )
        )

    def _check_right_quotes(self, docstring_node: ast.Constant) -> None:
        docstring_token = next(
            (
                token
                for token in self._file_tokens
                if token.start[0] == docstring_node.lineno
                and token.type == tokenize.STRING
            ),
        )

        if docstring_token.string.startswith(('"""', "'''")):
            # we don't check for the type of quotes, as this is up to the user or formatter
            return

        self.issues.append(
            Issue(
                line=docstring_node.lineno,
                column=docstring_node.col_offset,
                issue_number="317",
                message="A docstring should use triple quotes.",
            )
        )

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
        *,
        is_private: bool,
    ) -> None:
        docstring_node = self._get_docstring(node)
        if not is_private:
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
        # we don't use splitlines as we want the terminal line to be present
        lines = cast(str, docstring_node.value).split("\n")
        if not lines:
            return
        for check in (
            self._check_summary_in_first_line,
            self._check_summary_endswith_period,
            self._check_empty_line_after_summary,
            self._check_linebreak_at_end,
            self._check_docstring_start,
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

    def _check_docstring_start(
        self, docstring_node: ast.Constant, lines: list[str]
    ) -> None:
        if not lines[0]:
            return
        first_word = lines[0].split(" ")[0]
        if (
            # there is a first word which is not empty
            first_word
            # the first char is alphanumeric
            and first_word[0].isalnum()
            # the first char is either a digit or a letter which is either uppercase or
            # in the lowercase words
            and (
                first_word[0].isdigit()
                or (
                    first_word[0].isupper()
                    or first_word.lower() in self._options.docstyle_lowercase_words
                )
            )
        ):
            return
        self.issues.append(
            Issue(
                line=docstring_node.lineno,
                column=docstring_node.col_offset,
                issue_number="316",
                message="The summary should start with an uppercase letter or number.",
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

    def _check_linebreak_at_end(
        self, docstring_node: ast.Constant, lines: list[str]
    ) -> None:
        if len(lines) == 1:
            return
        if lines[-1].strip() == "":
            return
        self.issues.append(
            Issue(
                line=docstring_node.end_lineno or docstring_node.lineno,
                column=docstring_node.end_col_offset or docstring_node.col_offset,
                issue_number="315",
                message="A multiline docstring should end with a line break.",
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


@register_add_options
def add_options(option_manager: OptionManager) -> None:
    """Add options for this checker."""
    option_manager.add_option(
        "--docstyle-lowercase-words",
        parse_from_config=True,
        comma_separated_list=True,
        default=[],
    )


@register_parse_options
def parse_options(options: Namespace) -> None:
    """Parse options for this checker."""
    options.docstyle_lowercase_words = [
        option.lower() for option in options.docstyle_lowercase_words
    ]
