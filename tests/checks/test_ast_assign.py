"""Tests for _flake8_tergeo.ast_assign."""

from __future__ import annotations

from functools import partial

import pytest

from _flake8_tergeo import Issue
from _flake8_tergeo.checks import ast_assign
from tests.conftest import Flake8RunnerFixture

FTP090 = partial(Issue, issue_number="FTP090", message="Found unsorted __all__.")
FTP049 = partial(
    Issue, issue_number="FTP049", message="Found single element unpacking."
)
_FTP069 = partial(
    Issue,
    issue_number="FTP069",
    message="Using a variable named {name} can lead to confusion. "
    "Consider using another name.",
)
FTP094 = partial(
    Issue,
    issue_number="FTP094",
    message="__slots__ should be defined as a tuple or dict.",
)
FTP119 = partial(Issue, issue_number="FTP119", message="Found unsorted __slots__.")
FTP120 = partial(
    Issue,
    issue_number="FTP120",
    message="Found __slots__ assignment outside of a class.",
)
FTP124 = partial(
    Issue,
    issue_number="FTP124",
    message="__all__ should only be assigned on module level",
)
FTP126 = partial(
    Issue,
    issue_number="FTP126",
    message="TypeAlias is deprecated and the type statements should be used instead.",
)


def FTP069(  # pylint: disable=invalid-name
    *, line: int, column: int, name: str
) -> Issue:
    issue = _FTP069(line=line, column=column)
    return issue._replace(message=issue.message.format(name=name))


def test_ftp090(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp090_119.txt", issue_number="FTP090", name="__all__")
    assert results == [
        FTP090(line=15, column=1),
        FTP090(line=16, column=1),
        FTP090(line=18, column=1),
        FTP090(line=19, column=1),
        FTP090(line=21, column=1),
    ]


def test_ftp119(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp090_119.txt", issue_number="FTP119", name="__slots__")
    assert results == [
        FTP119(line=15, column=1),
        FTP119(line=16, column=1),
        FTP119(line=18, column=1),
        FTP119(line=19, column=1),
        FTP119(line=21, column=1),
    ]


def test_ftp049(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp049.txt", issue_number="FTP049")
    assert results == [
        FTP049(line=9, column=1),
        FTP049(line=10, column=1),
        FTP049(line=11, column=1),
    ]


@pytest.mark.parametrize("name", ast_assign.BAD_NAMES)
def test_ftp069(runner: Flake8RunnerFixture, name: str) -> None:
    results = runner(filename="ftp069.txt", issue_number="FTP069", name=name)
    assert results == [
        FTP069(line=7, column=1, name=name),
        FTP069(line=8, column=1, name=name),
    ]


def test_ftp094(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftp094.txt", issue_number="FTP094") == [
        FTP094(line=14, column=1),
        FTP094(line=15, column=1),
        FTP094(line=16, column=1),
        FTP094(line=17, column=1),
        FTP094(line=18, column=1),
        FTP094(line=19, column=1),
        FTP094(line=20, column=1),
    ]


def test_ftp120(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftp120.txt", issue_number="FTP120") == [
        FTP120(line=9, column=1),
        FTP120(line=10, column=1),
        FTP120(line=13, column=9),
    ]


def test_ftp124(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftp124.txt", issue_number="FTP124") == [
        FTP124(line=5, column=10),
        FTP124(line=6, column=12),
        FTP124(line=7, column=12),
    ]


@pytest.mark.parametrize(
    "imp,find_by_imp,type_alias",
    [
        ("from typing import TypeAlias", True, "TypeAlias"),
        ("import typing", True, "typing.TypeAlias"),
        ("import foo", False, "foo.TypeAlias"),
        ("from foo import TypeAlias", False, "TypeAlias"),
        ("from foo import typing", False, "typing.TypeAlias"),
    ],
)
@pytest.mark.parametrize(
    "version,find_by_version", [("3.7.0", False), ("3.12.0", True)]
)
def test_ftp126(
    runner: Flake8RunnerFixture,
    imp: str,
    find_by_imp: bool,
    type_alias: str,
    version: str,
    find_by_version: bool,
) -> None:
    results = runner(
        filename="ftp126.txt",
        issue_number="FTP126",
        imp=imp,
        type_alias=type_alias,
        args=("--ftp-python-version", version),
    )
    if find_by_imp and find_by_version:
        assert results == [FTP126(line=9, column=1)]
    else:
        assert not results
