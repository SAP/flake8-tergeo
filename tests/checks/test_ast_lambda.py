"""Tests for _flake8_tergeo.ast_lambda"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

_FTP079 = partial(
    Issue,
    issue_number="FTP079",
    message=("Found lambda statement which can be replaced with {func} function."),
)


def FTP079(  # pylint:disable=invalid-name
    *, line: int, column: int, func: str
) -> Issue:
    issue = _FTP079(column=column, line=line)
    return issue._replace(message=issue.message.format(func=func))


def test_ftp079(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp079.txt", issue_number="FTP079")
    assert results == [
        FTP079(line=8, column=1, func="list"),
        FTP079(line=9, column=1, func="tuple"),
        FTP079(line=10, column=1, func="dict"),
    ]
