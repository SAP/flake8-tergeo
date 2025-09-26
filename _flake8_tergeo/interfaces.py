"""Interfaces for flake8."""

from __future__ import annotations

import abc
from argparse import Namespace
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple

from _flake8_tergeo.type_definitions import IssueGenerator, OptionManager

if TYPE_CHECKING:

    # for typing we want to act as we would be subclassing the real flake8 OptionManager
    class AbstractOptionManager(OptionManager):
        """Abstract wrapper of flake8 OptionManager."""

        _option_manager: OptionManager

        def __init__(  # pylint: disable=super-init-not-called,unused-argument
            self, option_manager: OptionManager
        ) -> None: ...

else:

    # but at runtime we cannot subclass it as we only support a subset of its interface
    # and also want to force subclasses to implement the abstract methods
    class AbstractOptionManager(abc.ABC):
        """Abstract wrapper of flake8 OptionManager."""

        def __init__(self, option_manager: OptionManager) -> None:
            self._option_manager = option_manager

        @abc.abstractmethod
        def extend_default_ignore(self, disables: Sequence[str]) -> None:
            """Wrap flake8 OptionManager.extend_default_ignore."""

        @abc.abstractmethod
        def add_option(self, *args: Any, **kwargs: Any) -> None:
            """Wrap flake8 OptionManager.add_option."""


class AbstractNamespace(Namespace, abc.ABC):
    """Abstract wrapper around a Namespace object."""

    def __init__(self, args: Namespace) -> None:
        # pylint: disable=super-init-not-called
        # because we overwrite __setattr__ we need to workaround it in the __init__
        super().__setattr__("_args", args)

    @abc.abstractmethod
    def ftp_is_default(self, name: str) -> bool:
        """Checks if an option contains its default value.

        Note: this function is prefixed with ftp to avoid name clashes with other options.
        """


class AbstractChecker(abc.ABC):
    """Base class of all checks."""

    prefix: ClassVar[str]
    disabled: ClassVar[list[str]] = []

    @abc.abstractmethod
    def check(self) -> IssueGenerator:
        """Execute the check."""

    @classmethod
    def pre_parse_options(cls, options: AbstractNamespace) -> None:  # noqa: FTB027
        """Pre-processing of checker options."""


class Issue(NamedTuple):
    """Representation of an issue found by a checker."""

    line: int
    column: int
    issue_number: str
    message: str
