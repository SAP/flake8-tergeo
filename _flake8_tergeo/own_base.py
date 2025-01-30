"""Base classes for own-defined checks."""

from __future__ import annotations

import argparse
import ast
import tokenize
from collections.abc import Sequence
from threading import Event
from typing import Any, ClassVar

from typing_extensions import override

from _flake8_tergeo import flake8_types, registry
from _flake8_tergeo.interfaces import AbstractChecker, AbstractOptionManager


class OwnOptionManager(AbstractOptionManager):
    """OptionManager wrapper which is used for own-defined checks."""

    @override
    def extend_default_ignore(self, disables: list[str]) -> None:
        """Extend the default ignore.

        This method will add the self-defined check prefix before the error code.
        """
        new_disables = [f"{OwnChecker.prefix}{disable}" for disable in disables]
        self._option_manager.extend_default_ignore(new_disables)

    @override
    def add_option(self, *args: Any, **kwargs: Any) -> None:
        """Add an option."""
        self._option_manager.add_option(*args, **kwargs)


class OwnChecker(AbstractChecker):
    """Base class of all checks."""

    prefix = "P"
    options_added: ClassVar[Event] = Event()
    options_parsed: ClassVar[Event] = Event()

    @classmethod
    def add_options(cls, option_manager: flake8_types.OptionManager) -> None:
        """Handle flake8 add_options."""
        if cls.options_added.is_set():
            return
        wrapper = OwnOptionManager(option_manager)
        for func in registry.ADD_OPTIONS_REGISTRY:
            func(wrapper)
        cls.options_added.set()

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        """Handle flake8 parse_options."""
        if cls.options_parsed.is_set():
            return
        for func in registry.PARSE_OPTIONS_REGISTRY:
            func(options)
        cls.options_parsed.set()


class ASTChecker(OwnChecker):
    """Checker which uses the AST registry."""

    def __init__(self, tree: ast.AST):
        super().__init__()
        self._tree = tree

    @override
    def check(self) -> flake8_types.IssueGenerator:
        for node in ast.walk(self._tree):
            for func in registry.AST_REGISTRY[type(node)]:
                yield from func(node)


class TokenChecker(OwnChecker):
    """Checker which uses the token registry."""

    def __init__(self, file_tokens: Sequence[tokenize.TokenInfo]):
        super().__init__()
        self._file_tokens = file_tokens

    @override
    def check(self) -> flake8_types.IssueGenerator:
        for func in registry.TOKEN_REGISTRY:
            yield from func(self._file_tokens)
