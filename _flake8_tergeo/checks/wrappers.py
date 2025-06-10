"""Wrapper checks."""

from __future__ import annotations

import ast
from argparse import Namespace
from functools import lru_cache

from bugbear import BugBearChecker as _BugBearPlugin
from flake8_builtins import BuiltinsChecker as BuiltinsPlugin
from flake8_comprehensions import ComprehensionChecker as ComprehensionPlugin
from flake8_pytest_style.plugin import PytestStylePlugin
from flake8_simplify import Plugin as SimplifyPlugin
from flake8_typing_imports import Plugin as TypingImportPlugin
from typing_extensions import override

from _flake8_tergeo.flake8_types import IssueGenerator
from _flake8_tergeo.global_options import get_python_version
from _flake8_tergeo.interfaces import AbstractNamespace
from _flake8_tergeo.wrapper_base import BaseWrapperChecker


class BugBearPlugin(_BugBearPlugin):
    """BugBearPlugin with custom fixes."""

    @override
    @lru_cache  # noqa: FTP074
    def should_warn(self, code: str) -> bool:
        """Adjust should_warn.

        Normally, this function inspects the flake8 configuration.
        Since we want that all errors are always emitted, we override it.
        """
        return True


class BugBearChecker(BaseWrapperChecker):
    """Check wrapper for BugBearPlugin."""

    prefix = "B"
    old_prefix = "B"
    checker_class = BugBearPlugin
    disabled = ["001", "950", "019"]

    def __init__(
        self, tree: ast.AST, filename: str, max_line_length: int, options: Namespace
    ) -> None:
        super().__init__(
            BugBearPlugin(
                tree=tree,
                filename=filename,
                max_line_length=max_line_length,
                options=options,
            )
        )

    @override
    def check(self) -> IssueGenerator:
        """Execute the check."""
        for issue in super().check():
            # B905 runs on < 3.10: https://github.com/PyCQA/flake8-bugbear/issues/320
            if issue.issue_number == "905" and get_python_version() < (3, 10):
                continue
            yield issue


class ComprehensionsChecker(BaseWrapperChecker):
    """Check wrapper for ComprehensionPlugin."""

    prefix = "C"
    old_prefix = "C"
    checker_class = ComprehensionPlugin

    def __init__(self, tree: ast.AST) -> None:
        super().__init__(ComprehensionPlugin(tree))

    @override
    def check(self) -> IssueGenerator:
        """Execute the check."""
        yield from super().check()


class BuiltinsChecker(BaseWrapperChecker):
    """Check wrapper for BuiltinsPlugin."""

    prefix = "U"
    old_prefix = "A"
    checker_class = BuiltinsPlugin

    def __init__(self, tree: ast.AST, filename: str) -> None:
        super().__init__(BuiltinsPlugin(tree=tree, filename=filename))

    @override
    def check(self) -> IssueGenerator:
        """Execute the check."""
        yield from super().check()


class SimplifyChecker(BaseWrapperChecker):
    """Check wrapper for SimplifyPlugin."""

    prefix = "M"
    old_prefix = "SIM"
    checker_class = SimplifyPlugin
    disabled = ["116", "901"]

    def __init__(self, tree: ast.AST) -> None:
        super().__init__(SimplifyPlugin(tree=tree))

    @override
    def check(self) -> IssueGenerator:
        """Execute the check."""
        yield from super().check()


class PytestStyleChecker(BaseWrapperChecker):
    """Check wrapper for PytestStylePlugin."""

    prefix = "T"
    old_prefix = "PT"
    checker_class = PytestStylePlugin
    disabled = ["004", "005", "013", "019"]

    def __init__(self, tree: ast.AST) -> None:
        super().__init__(PytestStylePlugin(tree=tree))

    @override
    def check(self) -> IssueGenerator:
        """Execute the check."""
        yield from super().check()


class TypingImportChecker(BaseWrapperChecker):
    """Check wrapper for TypingImportPlugin."""

    prefix = "Y"
    old_prefix = "TYP"
    checker_class = TypingImportPlugin

    def __init__(self, tree: ast.AST) -> None:
        super().__init__(TypingImportPlugin(tree=tree))

    @override
    def check(self) -> IssueGenerator:
        """Execute the check."""
        yield from super().check()

    @classmethod
    @override
    def pre_parse_options(cls, options: AbstractNamespace) -> None:
        """Pre-processing of plugin options."""
        if options.ftp_is_default("min_python_version"):
            options.min_python_version = options.python_version
