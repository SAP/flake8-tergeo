"""Tests for _flake8_tergeo.checker.ast_class_def"""

from __future__ import annotations

from functools import partial

import pytest
from dirty_equals import IsOneOf

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture
from tests.util import LenientIssue

FTP066 = partial(
    Issue,
    issue_number="FTP066",
    message="Instead of extending both Enum and int, use enum.IntEnum instead.",
)
FTP067 = partial(
    Issue,
    issue_number="FTP067",
    message="Instead of extending both Enum and str, use enum.StrEnum instead.",
)
FTP009 = partial(
    Issue,
    issue_number="FTP009",
    message="Found class extending BaseException. Use Exception instead.",
)
_FTP082 = partial(
    Issue,
    issue_number="FTP082",
    message="Unnecessary use of abstract metaclass. Use {clazz}(abc.ABC) instead.",
)
_FTP097 = partial(
    Issue,
    issue_number="FTP097",
    message="Enum '{enum}' is missing the unique decorator.",
)
FTP074 = partial(
    LenientIssue,
    issue_number="FTP074",
    message="Using a cache function on a method can lead to memory leaks.",
)
_FTP005 = partial(
    Issue,
    issue_number="FTP005",
    message=(
        "Found duplicated class field {field}. "
        "If a calculation is needed, refactor the code out to a function "
        "and use only one assign statement."
    ),
)
FTP128 = partial(
    Issue,
    issue_number="FTP128",
    message="Use the new generic syntax instead of Generic.",
)


def FTP082(line: int, column: int, clazz: str) -> Issue:  # pylint:disable=invalid-name
    issue = _FTP082(line=line, column=column)
    return issue._replace(message=issue.message.format(clazz=clazz))


def FTP097(line: int, column: int, enum: str) -> Issue:  # pylint:disable=invalid-name
    issue = _FTP097(line=line, column=column)
    return issue._replace(message=issue.message.format(enum=enum))


def FTP005(line: int, column: int, field: str) -> Issue:  # pylint:disable=invalid-name
    issue = _FTP005(line=line, column=column)
    return issue._replace(message=issue.message.format(field=field))


def test_ftp009(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftp009.txt", issue_number="FTP009") == [
        FTP009(line=7, column=11),
        FTP009(line=8, column=21),
    ]


class TestFTP074:
    def test_ftp074_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp074_ignore.txt", issue_number="FTP074")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import functools", "functools.cache"),
            ("import functools", "functools.lru_cache"),
            ("import functools", "functools.lru_cache(maxsize=123)"),
            ("from functools import cache", "cache"),
            ("from functools import lru_cache", "lru_cache"),
            ("from functools import lru_cache", "lru_cache(maxsize=None)"),
        ],
    )
    def test_ftp074(self, runner: Flake8RunnerFixture, imp: str, func: str) -> None:
        results = runner(
            filename="ftp074.txt", issue_number="FTP074", imp=imp, func=func
        )
        assert results == [FTP074(line=15, column=IsOneOf(5, 6))]


class TestFTP097:
    def test_ftp097_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp097_ignore.txt", issue_number="FTP097")

    @pytest.mark.parametrize(
        "imp,unique,enum",
        [
            ("from enum import Enum, unique", "unique", "Enum"),
            ("from enum import StrEnum, unique", "unique", "StrEnum"),
            ("import enum", "enum.unique", "enum.Enum"),
            ("import enum", "enum.unique", "enum.IntEnum"),
        ],
    )
    def test_ftp097(
        self, runner: Flake8RunnerFixture, imp: str, unique: str, enum: str
    ) -> None:
        results = runner(
            filename="ftp097.txt",
            issue_number="FTP097",
            imp=imp,
            unique=unique,
            enum=enum,
        )
        assert results == [FTP097(line=8, column=1, enum="Foo")]


class TestFTP082:
    def test_ftp082_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp082_ignore.txt", issue_number="FTP082")

    @pytest.mark.parametrize(
        "imp,metaclass",
        [
            ("import abc", "abc.ABCMeta"),
            ("from abc import ABCMeta", "ABCMeta"),
        ],
    )
    def test_ftp082(
        self, runner: Flake8RunnerFixture, imp: str, metaclass: str
    ) -> None:
        results = runner(
            filename="ftp082.txt", issue_number="FTP082", imp=imp, metaclass=metaclass
        )
        assert results == [FTP082(line=3, column=1, clazz="Foo")]


class TestFTP066:
    def test_ftp066_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp066_ignore.txt", issue_number="FTP066")

    @pytest.mark.parametrize(
        "imp,enum",
        [("import enum", "enum.Enum"), ("from enum import Enum", "Enum")],
    )
    def test_ftp066(self, runner: Flake8RunnerFixture, imp: str, enum: str) -> None:
        results = runner(
            filename="ftp066.txt", issue_number="FTP066", imp=imp, enum=enum
        )
        assert results == [
            FTP066(line=6, column=1),
            FTP066(line=9, column=1),
            FTP066(line=12, column=1),
        ]


class TestFTP067:
    params = pytest.mark.parametrize(
        "imp,enum",
        [("import enum", "enum.Enum"), ("from enum import Enum", "Enum")],
    )

    def test_ftp067_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(
            filename="ftp067_ignore.txt",
            issue_number="FTP067",
            args=("--ftp-python-version", "3.11.0"),
        )

    @params
    def test_ftp067_310(self, runner: Flake8RunnerFixture, imp: str, enum: str) -> None:
        assert not runner(
            filename="ftp067.txt",
            issue_number="FTP067",
            args=("--ftp-python-version", "3.10.0"),
            imp=imp,
            enum=enum,
        )

    @params
    def test_ftp067_311(self, runner: Flake8RunnerFixture, imp: str, enum: str) -> None:
        results = runner(
            filename="ftp067.txt",
            issue_number="FTP067",
            args=("--ftp-python-version", "3.11.0"),
            imp=imp,
            enum=enum,
        )
        assert results == [
            FTP067(line=6, column=1),
            FTP067(line=9, column=1),
            FTP067(line=12, column=1),
        ]


def test_ftp005(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftp005.txt", issue_number="FTP005") == [
        FTP005(line=28, column=5, field="a"),
        FTP005(line=29, column=5, field="c"),
        FTP005(line=31, column=5, field="a"),
        FTP005(line=32, column=5, field="x"),
    ]


@pytest.mark.parametrize(
    "imp,find_by_imp,generic",
    [
        ("from typing import Generic", True, "Generic"),
        ("import typing", True, "typing.Generic"),
        ("import foo", False, "foo.Generic"),
        ("from foo import Generic", False, "Generic"),
        ("from foo import typing", False, "typing.Generic"),
    ],
)
@pytest.mark.parametrize(
    "version,find_by_version", [("3.7.0", False), ("3.12.0", True)]
)
def test_ftp128(
    runner: Flake8RunnerFixture,
    imp: str,
    find_by_imp: bool,
    generic: str,
    version: str,
    find_by_version: bool,
) -> None:
    results = runner(
        filename="ftp128.txt",
        issue_number="FTP128",
        imp=imp,
        generic=generic,
        args=("--ftp-python-version", version),
    )
    if find_by_imp and find_by_version:
        assert results == [
            FTP128(line=10, column=9),
            FTP128(line=11, column=9),
            FTP128(line=12, column=15),
        ]
    else:
        assert not results
