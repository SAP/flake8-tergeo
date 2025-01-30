"""Interfaces for flake8."""

from __future__ import annotations

import abc
from argparse import Namespace
from typing import Any, ClassVar

from _flake8_tergeo import flake8_types


class AbstractNamespace(Namespace, abc.ABC):
    """Abstract wrapper around a Namespace object."""

    def __init__(self, args: Namespace) -> None:
        # pylint: disable=super-init-not-called
        # because we overwrite __setattr__ we need to workaround it in the __init__
        super().__setattr__("_args", args)

    @abc.abstractmethod
    def ftp_is_default(self, name: str) -> bool:
        """Checks if an option contains its default value.

        Note: this function is named by purpose terf, which stands for tergeo function,
        to avoid name clashes with other options.
        """


class AbstractOptionManager(abc.ABC):
    """Abstract wrapper of flake8 OptionManager."""

    def __init__(self, option_manager: flake8_types.OptionManager) -> None:
        self._option_manager = option_manager

    @abc.abstractmethod
    def extend_default_ignore(self, disables: list[str]) -> None:
        """Wrap flake8 OptionManager.extend_default_ignore."""

    @abc.abstractmethod
    def add_option(self, *args: Any, **kwargs: Any) -> None:
        """Wrap flake8 OptionManager.add_option."""


class AbstractChecker(abc.ABC):
    """Base class of all checks."""

    prefix: ClassVar[str]
    disabled: ClassVar[list[str]] = []

    @abc.abstractmethod
    def check(self) -> flake8_types.IssueGenerator:
        """Execute the check."""

    @classmethod
    def pre_parse_options(cls, options: AbstractNamespace) -> None:  # noqa: FTB027
        """Pre-processing of checker options."""
