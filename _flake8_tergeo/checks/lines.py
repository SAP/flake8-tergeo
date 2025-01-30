"""Line based checks."""

from __future__ import annotations

import importlib.resources
import re

from typing_extensions import override

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.own_base import OwnChecker

_PATTERN = re.compile("\u202a|\u202b|\u202d|\u202e|\u2066|\u2067|\u2068|\u202c|\u2069")


def _load_invisible_chars_file() -> str:
    # data source: https://github.com/hediet/vscode-unicode-data
    # usage: https://github.com/microsoft/vscode/blob/main/src/vs/base/common/strings.ts
    pkg = importlib.resources.files("_flake8_tergeo")
    return (pkg / "checks" / "ftp115_invisible_chars.txt").read_text(encoding="utf-8")


class LineChecker(OwnChecker):
    """Check for directionality formatting unicode characters."""

    def __init__(self, lines: list[str]) -> None:
        super().__init__()
        self._lines = lines
        self._invisible_unicode = [
            int(x) for x in _load_invisible_chars_file().split("\n") if x
        ]

    @override
    def check(self) -> IssueGenerator:
        """Check the provided lines."""
        for lineno, line in enumerate(self._lines, start=1):
            yield from self._check_bidi(line, lineno)
            yield from self._check_invisible_unicode(line, lineno)

    def _check_bidi(self, line: str, lineno: int) -> IssueGenerator:
        """Checks for bidi unicode characters leading to issues in source code.

        See `this paper <https://trojansource.codes/trojan-source.pdf>`_ for reference.
        """
        for match in _PATTERN.finditer(line):
            char = match.group().encode("unicode-escape").decode("ascii")
            yield Issue(
                line=lineno,
                column=match.start(),
                issue_number="006",
                message=f"Found directionality formatting unicode character '{char}'.",
            )

    def _check_invisible_unicode(self, line: str, lineno: int) -> IssueGenerator:
        for column, char in enumerate(line, start=1):
            ordinal = ord(char)
            if ordinal in self._invisible_unicode:
                yield Issue(
                    line=lineno,
                    column=column,
                    issue_number="115",
                    message=f"Found invisible unicode character {ordinal}. "
                    f"If the character is there by purpose, use '\\u{ordinal:04x}'.",
                )
