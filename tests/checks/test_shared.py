"""Tests for _flake8_tergeo.checks.shared."""

from __future__ import annotations

import sys
from functools import partial

import pytest

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP077 = partial(
    Issue,
    issue_number="FTP077",
    message="None should be the last value in an annotation.",
)
FTP104 = partial(
    Issue,
    issue_number="FTP104",
    message="Bottom types (Never/NoReturn) should not be used in unions.",
)


class TestFTP077:
    def test(self, runner: Flake8RunnerFixture) -> None:
        results = runner(filename="ftp077.txt", issue_number="FTP077")
        assert results == [
            FTP077(line=22, column=10),
            FTP077(line=23, column=4),
            FTP077(line=24, column=14),
            FTP077(line=24, column=25),
            FTP077(line=26, column=20),
            FTP077(line=26, column=46),
            FTP077(line=27, column=14),
            FTP077(line=28, column=16),
            FTP077(line=29, column=10),
        ]

    @pytest.mark.skipif(
        sys.version_info < (3, 12), reason="type statement was added in 3.12"
    )
    def test_type_statement(self, runner: Flake8RunnerFixture) -> None:
        results = runner(filename="ftp077_type.txt", issue_number="FTP077")
        assert results == [
            FTP077(line=8, column=10),
            FTP077(line=9, column=16),
        ]


class TestFTP104:

    @pytest.mark.parametrize(
        "imp,class_",
        [("from foo import Never", "Never"), ("import typ", "typ.NoReturn")],
    )
    def test_ignore(self, runner: Flake8RunnerFixture, imp: str, class_: str) -> None:
        assert not runner(filename="ftp104.txt", issue_number="FTP104")

    @pytest.mark.parametrize(
        "imp,class_",
        [
            ("from typing import Never", "Never"),
            ("from typing import NoReturn", "NoReturn"),
            ("import typing", "typing.Never"),
            ("import typing", "typing.NoReturn"),
        ],
    )
    def test(self, runner: Flake8RunnerFixture, imp: str, class_: str) -> None:
        results = runner(
            filename="ftp104.txt", issue_number="FTP104", imp=imp, class_=class_
        )
        assert results == [
            FTP104(line=13, column=4),
            FTP104(line=14, column=5),
            FTP104(line=15, column=16),
            FTP104(line=16, column=4),
        ]

    @pytest.mark.skipif(
        sys.version_info < (3, 12), reason="type statement was added in 3.12"
    )
    def test_type_statement(self, runner: Flake8RunnerFixture) -> None:
        results = runner(filename="ftp104_type.txt", issue_number="FTP104")
        assert results == [
            FTP104(line=7, column=10),
            FTP104(line=8, column=10),
        ]
