"""Base classes for externally defined checks."""

from __future__ import annotations

import abc
import argparse
from collections.abc import Sequence
from typing import Any, ClassVar

from typing_extensions import override

from _flake8_tergeo import util
from _flake8_tergeo.interfaces import AbstractChecker, AbstractOptionManager, Issue
from _flake8_tergeo.type_definitions import IssueGenerator, OptionManager


class WrapperOptionManager(AbstractOptionManager):
    """Wrapper of flake8 OptionManager on checker level."""

    def __init__(
        self,
        option_manager: OptionManager,
        old_prefix: str,
        new_prefix: str,
    ) -> None:
        super().__init__(option_manager)
        self._old_prefix = old_prefix
        self._new_prefix = new_prefix

    @override
    def extend_default_ignore(self, error_codes: Sequence[str]) -> None:
        """Wrap flake8 OptionManager.extend_default_ignore.

        This method replaces the error code prefix.
        """
        new_error_codes = []
        for error_code in error_codes:
            trimmed_prefix = error_code[len(self._old_prefix) :]
            new_error_codes.append(f"{self._new_prefix}{trimmed_prefix}")
        self._option_manager.extend_default_ignore(new_error_codes)

    @override
    def add_option(self, *args: Any, **kwargs: Any) -> None:
        """Wrap flake8 OptionManager.add_option.

        This is a simple forward to the wrapped option manager.
        """
        self._option_manager.add_option(*args, **kwargs)


class BaseWrapperChecker(AbstractChecker):
    """Base class of all checks which wrap a flake8 plugin."""

    checker_class: ClassVar[type[Any]]
    old_prefix: ClassVar[str]

    def __init__(self, checker: Any) -> None:
        self._checker = checker

    @classmethod
    def add_options(cls, option_manager: OptionManager) -> None:
        """Handle flake8 add_options."""
        if util.has_add_options(cls.checker_class):
            wrapper = WrapperOptionManager(option_manager, cls.old_prefix, cls.prefix)
            cls.checker_class.add_options(wrapper)

    @classmethod
    def parse_options(
        cls,
        option_manager: OptionManager,
        options: argparse.Namespace,
        args: list[str],
    ) -> None:
        """Handle flake8 parse_options."""
        if util.has_parse_options(cls.checker_class):
            if util.is_complex_parse_options(cls.checker_class):
                cls.checker_class.parse_options(option_manager, options, args)
            else:
                cls.checker_class.parse_options(options)

    @override
    @abc.abstractmethod
    def check(self) -> IssueGenerator:
        generator = self._checker.run()

        for finding in generator:
            trimmed_prefix = finding[2][len(self.old_prefix) :]
            issue_number, message = trimmed_prefix.split(" ", maxsplit=1)
            message += f" (originally reported as {self.old_prefix}{issue_number})"

            yield Issue(
                line=finding[0],
                column=finding[1],
                issue_number=issue_number,
                message=message,
            )
