"""Tests for _flake8_tergeo.logging"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP031 = partial(
    Issue,
    issue_number="FTP031",
    message="percentage formatting should be replaced with printf-style formatting.",
)
FTP032 = partial(
    Issue,
    issue_number="FTP032",
    message="f-string should be replaced with printf-style formatting.",
)
FTP033 = partial(
    Issue,
    issue_number="FTP033",
    message="str.format should be replaced with printf-style formatting.",
)
FTP034 = partial(
    Issue,
    issue_number="FTP034",
    message="Using exec_info=True in exception() is redundant.",
)
FTP035 = partial(
    Issue, issue_number="FTP035", message="warn() is deprecated. Use warning() instead."
)
FTP036 = partial(
    Issue,
    issue_number="FTP036",
    message="Using exec_info=True in error() can be simplified to exception().",
)
_FTP037 = partial(
    Issue,
    issue_number="FTP037",
    message="The extra key '{key}' clashes with existing log record fields.",
)


def FTP037(*, line: int, column: int, key: str) -> Issue:  # pylint:disable=invalid-name
    issue = _FTP037(line=line, column=column)
    return issue._replace(message=issue.message.format(key=key))


def test_ftp031(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp031.txt", issue_number="FTP031")
    assert results == [FTP031(line=13, column=1), FTP031(line=14, column=1)]


def test_ftp032(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp032.txt", issue_number="FTP032")
    assert results == [FTP032(line=10, column=1), FTP032(line=11, column=1)]


def test_ftp033(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp033.txt", issue_number="FTP033")
    assert results == [
        FTP033(line=12, column=1),
        FTP033(line=13, column=1),
        FTP033(line=14, column=1),
    ]


def test_ftp034(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp034.txt", issue_number="FTP034")
    assert results == [FTP034(line=10, column=1)]


def test_ftp035(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp035.txt", issue_number="FTP035")
    assert results == [FTP035(line=10, column=1)]


def test_ftp036(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp036.txt", issue_number="FTP036")
    assert results == [FTP036(line=8, column=1)]


def test_ftp037(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp037.txt", issue_number="FTP037")
    assert results == [
        FTP037(line=10, column=43, key="msg"),
        FTP037(line=11, column=43, key="threadName"),
    ]
