"""Flake8 plugin base module."""

from __future__ import annotations

import ast
import inspect
import tokenize
from collections.abc import Generator, Sequence
from importlib.metadata import version
from typing import Any, ClassVar, TypeVar

from typing_extensions import override

from _flake8_tergeo import util
from _flake8_tergeo.ast_util import set_info_in_tree
from _flake8_tergeo.flake8_types import OptionManager
from _flake8_tergeo.interfaces import (
    AbstractChecker,
    AbstractNamespace,
    AbstractOptionManager,
)

_BASE_PREFIX = "FT"
_PLUGIN: Flake8TergeoPlugin | None = None
T = TypeVar("T")


def _get_concrete_classes(base_class: type[T]) -> list[type[T]]:
    subclasses = []
    for subclass in base_class.__subclasses__():
        if not inspect.isabstract(subclass):
            subclasses.append(subclass)
        subclasses += _get_concrete_classes(subclass)
    return subclasses


def get_plugin() -> Flake8TergeoPlugin:
    """Return the current plugin instance."""
    if not _PLUGIN:
        raise AssertionError("The flake8-tergeo plugin was not correctly initialized")
    return _PLUGIN


class DefaultWrapper:
    """Wrapper for default values."""

    def __init__(self, default: Any) -> None:
        self._default = default

    @property
    def default(self) -> Any:
        """Return the default value."""
        return self._default

    @override
    def __eq__(self, value: object) -> bool:
        return isinstance(value, DefaultWrapper) and value.default == self.default

    @override
    def __hash__(self) -> int:
        return hash(self.default)


class BaseOptionManager(AbstractOptionManager):
    """Wrapper of flake8 OptionManager on plugin level."""

    @override
    def extend_default_ignore(self, disables: list[str]) -> None:
        """Extend the default ignore.

        This method adds the plugin prefix before the error code.
        """
        new_disables = [f"{_BASE_PREFIX}{disable}" for disable in disables]
        self._option_manager.extend_default_ignore(new_disables)

    @override
    def add_option(self, *args: Any, **kwargs: Any) -> None:
        """Add an option.

        This method adds the plugin prefix before the original option name.
        """
        args_list = list(args)
        if not args_list[0].startswith("--"):
            raise ValueError(f"Unable to handle first argument {args_list[0]}")

        if "default" in kwargs:
            kwargs["default"] = DefaultWrapper(kwargs["default"])

        args_list[0] = f"--ftp-{args_list[0][2:]}"
        self._option_manager.add_option(*args_list, **kwargs)


class BaseNamespace(AbstractNamespace):
    """argparse.BaseNamespace wrapper."""

    @override
    def __getattr__(self, name: str) -> Any:
        """Returns the stored argument after adding `ftp_` to it."""
        if name not in (
            "select",
            "extend_select",
            "extended_default_select",
            "ignore",
            "extend_ignore",
            "extended_default_ignore",
            "enable_extensions",
        ):
            name = f"ftp_{name}"
        value = getattr(self._args, name)
        return value.default if isinstance(value, DefaultWrapper) else value

    @override
    def ftp_is_default(self, name: str) -> bool:
        value = getattr(self._args, f"ftp_{name}")
        return isinstance(value, DefaultWrapper)

    @override
    def __setattr__(self, __name: str, __value: Any) -> None:
        setattr(self._args, f"ftp_{__name}", __value)


class Flake8TergeoPlugin:
    """flake8-tergeo flake8 plugin."""

    name: ClassVar[str] = "flake8-tergeo"
    version: ClassVar[str] = version("flake8-tergeo")
    off_by_default: ClassVar[bool] = True
    module_load_error: ClassVar[ImportError | None] = None

    _setup_performed: ClassVar[bool] = False

    _parse_options_option_manager: ClassVar[OptionManager | None] = None
    _parse_options_options: ClassVar[BaseNamespace | None] = None
    _parse_options_args: ClassVar[list[str] | None] = None

    def __init__(
        self,
        tree: ast.AST,
        filename: str,
        max_line_length: int,
        file_tokens: Sequence[tokenize.TokenInfo],
        lines: list[str],
    ) -> None:
        set_info_in_tree(tree)
        self._args = {
            "tree": tree,
            "max_line_length": max_line_length,
            "filename": filename,
            "file_tokens": file_tokens,
            "lines": lines,
        }
        self.filename = filename

        global _PLUGIN
        _PLUGIN = self

    @classmethod
    def _setup_once(cls) -> None:
        if cls._setup_performed:
            return
        if cls.get_options().auto_manage_options:
            for checker in _get_concrete_classes(AbstractChecker):
                checker.pre_parse_options(cls.get_options())
        for checker in _get_concrete_classes(AbstractChecker):
            cls._run_parse_options(checker)
        cls._setup_performed = True

    def run(self) -> Generator[tuple[int, int, str, type[Any]]]:
        """Execute all checks."""
        if self.module_load_error:
            yield (
                -1,
                -1,
                f"FTP000 Cannot load plugin due '{self.module_load_error}'",
                type(self),
            )
            return  # don't check anything else

        self._setup_once()
        self._args["options"] = self.get_options()

        for checker in _get_concrete_classes(AbstractChecker):
            kwargs = self._build_arguments_for_run(checker)

            for issue in checker(**kwargs).check():
                if issue.issue_number in checker.disabled:
                    continue
                prefix = checker.prefix
                message = f"{_BASE_PREFIX}{prefix}{issue.issue_number} {issue.message}"
                yield (issue.line, issue.column, message, type(self))

    @classmethod
    def get_options(cls) -> BaseNamespace:
        """Get the parsed options."""
        if not cls._parse_options_options:
            raise AssertionError("The options were not parsed yet")
        return cls._parse_options_options

    @classmethod
    def _run_parse_options(cls, checker: type[AbstractChecker]) -> None:
        if util.has_parse_options(checker):
            if util.is_complex_parse_options(checker):
                checker.parse_options(  # type:ignore[attr-defined]
                    cls._parse_options_option_manager,
                    cls._parse_options_options,
                    cls._parse_options_args,
                )
            else:
                checker.parse_options(  # type:ignore[attr-defined]
                    cls._parse_options_options
                )

    def _build_arguments_for_run(
        self, checker: type[AbstractChecker]
    ) -> dict[str, Any]:
        argsspec = inspect.getfullargspec(checker.__init__)
        return util.build_args(argsspec, self._args)

    @classmethod
    def add_options(cls, option_manager: OptionManager) -> None:
        """Handle flake8 options."""
        option_manager = BaseOptionManager(option_manager)

        for checker in _get_concrete_classes(AbstractChecker):
            if util.has_add_options(checker):
                checker.add_options(option_manager)  # type:ignore[attr-defined]

    @classmethod
    def parse_options(
        cls,
        option_manager: OptionManager,
        options: BaseNamespace,
        args: list[str],
    ) -> None:
        """Handle flake8 parse_options."""
        cls._parse_options_option_manager = BaseOptionManager(option_manager)
        cls._parse_options_options = BaseNamespace(options)
        cls._parse_options_args = args
        # We don't call parse_options on the checkers because external ones might set data on
        # class level. Therefore parse_options is twice executed, once for TER and once directly
        # for the external plugin leading to confusion
