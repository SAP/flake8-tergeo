"""Tests for _flake8_tergeo.checks.ast_bin_op"""

from __future__ import annotations

from functools import partial

import pytest

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP060 = partial(
    Issue,
    issue_number="FTP060",
    message="String literal formatting using percent operator.",
)
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


def test_ftp060(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp060.txt", issue_number="FTP060")
    assert results == [
        FTP060(line=6, column=1),
        FTP060(line=7, column=1),
        FTP060(line=8, column=1),
    ]


def test_ftp077(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp077.txt", issue_number="FTP077")
    assert results == [
        FTP077(line=16, column=10),
        FTP077(line=17, column=4),
        FTP077(line=18, column=14),
        FTP077(line=18, column=25),
        FTP077(line=20, column=20),
        FTP077(line=20, column=46),
        FTP077(line=21, column=14),
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
            FTP104(line=8, column=4),
            FTP104(line=9, column=5),
        ]
