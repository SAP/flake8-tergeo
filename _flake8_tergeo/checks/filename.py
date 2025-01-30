"""File based checks."""

from __future__ import annotations

import re
from pathlib import Path

from typing_extensions import override

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.own_base import OwnChecker

_PATTERN = re.compile("^[0-9a-z_]+$")
_ENCODING = re.compile(r"^\s*#.*?coding[:=]")


class FileNameChecker(OwnChecker):
    """Check common issue in files."""

    def __init__(self, filename: str) -> None:
        super().__init__()
        self._path = Path(filename)

        basename = self._path.stem
        self._name = self._path.parent.stem if basename == "__init__" else basename
        self._type = "package" if basename == "__init__" else "file"

    @override
    def check(self) -> IssueGenerator:
        """Check the provided file."""
        yield from self._check_filename()
        yield from self._check_encoding_comment()
        yield from self._check_implicit_namespace()

    def _check_encoding_comment(self) -> IssueGenerator:
        with self._path.open(encoding="utf-8") as file_handle:
            for lineno, line in enumerate(file_handle):
                if _ENCODING.match(line):
                    yield Issue(
                        line=lineno + 1,
                        column=0,
                        issue_number="020",
                        message="Found encoding comment.",
                    )

    def _check_implicit_namespace(self) -> IssueGenerator:
        if not (self._path.parent / "__init__.py").exists():
            yield Issue(
                line=1,
                column=0,
                issue_number="040",
                message="File is part of an implicit namespace package.",
            )

    def _check_filename(self) -> IssueGenerator:
        if not _PATTERN.match(self._name):
            yield Issue(
                line=1,
                column=0,
                issue_number="004",
                message=f"Name of {self._type} '{self._name}' is invalid.",
            )
