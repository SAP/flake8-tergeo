"""Types for flake8 checks and plugins."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any, NamedTuple

from typing_extensions import Protocol


class Issue(NamedTuple):
    """Representation of an issue found by a checker."""

    line: int
    column: int
    issue_number: str
    message: str


IssueGenerator = Generator[Issue]


class OptionManager(Protocol):
    """Protocol for flake8 OptionManager."""

    def extend_default_ignore(self, disables: list[str]) -> None:
        """The extend_default_ignore method of flake8."""

    def add_option(self, *args: Any, **kwargs: Any) -> None:
        """The add_option method of flake8."""
