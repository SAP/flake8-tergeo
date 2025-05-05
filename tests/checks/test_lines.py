"""Tests for _flake8_tergeo.lines"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

_FTP006 = partial(
    Issue,
    issue_number="FTP006",
    message="Found directionality formatting unicode character '{char}'.",
)
_FTP115 = partial(
    Issue,
    issue_number="FTP115",
    message="Found invisible unicode character {code_point}. "
    "If the character is there by purpose, use '{replacement}'.",
)


def FTP006(  # pylint:disable=invalid-name
    *, line: int, column: int, char: str
) -> Issue:
    issue = _FTP006(line=line, column=column)
    return issue._replace(message=issue.message.format(char=char))


def FTP115(  # pylint:disable=invalid-name
    *, line: int, column: int, code_point: int, replacement: str
) -> Issue:
    issue = _FTP115(line=line, column=column)
    return issue._replace(
        message=issue.message.format(code_point=code_point, replacement=replacement)
    )


def test_ftp006(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp006.txt", issue_number="FTP006")
    assert results == [FTP006(line=4, column=47, char="\\u2067")]


def test_ftp115(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp115.txt", issue_number="FTP115")
    assert results == [
        FTP115(line=7, column=10, code_point=173, replacement="\\u00ad"),
        FTP115(line=8, column=7, code_point=847, replacement="\\u034f"),
    ]
