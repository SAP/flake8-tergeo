# pylint: disable=invalid-name

"""Tests for _flake8_tergeo.wrappers."""

from __future__ import annotations

import pytest
from dirty_equals import IsOneOf
from pytest_mock import MockerFixture

from _flake8_tergeo.checks.wrappers import BugBearChecker, TypingImportChecker
from _flake8_tergeo.flake8_types import Issue
from _flake8_tergeo.interfaces import AbstractNamespace
from tests.conftest import Flake8RunnerFixture
from tests.util import LenientIssue


def test_ComprehensionsChecker(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftc.txt", issue_number="FTC") == [
        LenientIssue(
            line=1,
            column=IsOneOf(5, 6),
            issue_number="FTC416",
            message=(
                "Unnecessary list comprehension - rewrite using list(). "
                "(originally reported as C416)"
            ),
        )
    ]


def test_BuiltinsChecker(runner: Flake8RunnerFixture) -> None:
    result = runner(filename="ftu.txt", issue_number="FTU")
    result = [issue._replace(message=issue.message.lower()) for issue in result]
    assert result == [
        Issue(
            column=1,
            line=1,
            issue_number="FTU001",
            message=(
                'variable "copyright" is shadowing a Python builtin (originally reported as A001)'
            ).lower(),
        )
    ]


class TestBugBearChecker:

    def test(self, runner: Flake8RunnerFixture) -> None:
        assert runner(filename="ftb.txt", issue_number="FTB") == [
            Issue(
                line=1,
                column=5,
                issue_number="FTB009",
                message=(
                    "Do not call getattr with a constant attribute value, it is not any safer "
                    "than normal property access. (originally reported as B009)"
                ),
            )
        ]

    def test_905_disabled(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(
            filename="ftb_905.txt",
            issue_number="FTB",
            args=("--ftp-python-version", "3.7.1"),
        )

    def test_905_enabled(self, runner: Flake8RunnerFixture) -> None:
        assert runner(
            filename="ftb_905.txt",
            issue_number="FTB",
            args=("--ftp-python-version", "3.10.1"),
        ) == [
            Issue(
                line=1,
                column=1,
                issue_number="FTB905",
                message=(
                    "`zip()` without an explicit `strict=` parameter. (originally reported as B905)"
                ),
            )
        ]

    def test_pre_parse_options_with_extend_immutable_calls(
        self, mocker: MockerFixture
    ) -> None:
        options = mocker.Mock(spec=AbstractNamespace)
        options.ftp_is_default.return_value = False
        BugBearChecker.pre_parse_options(options)
        assert not hasattr(options, "extend_immutable_calls")


def test_SimplifyChecker(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftm.txt", issue_number="FTM") == [
        Issue(
            column=4,
            line=1,
            issue_number="FTM201",
            message="Use 'a != b' instead of 'not a == b' (originally reported as SIM201)",
        )
    ]


def test_PytestStyleChecker(runner: Flake8RunnerFixture) -> None:
    assert runner(filename="ftt.txt", issue_number="FTT") == [
        Issue(
            column=2,
            line=1,
            issue_number="FTT001",
            message="use @pytest.fixture over @pytest.fixture() (originally reported as PT001)",
        )
    ]


class TestTypingImportChecker:

    def test(self, runner: Flake8RunnerFixture) -> None:
        assert runner(filename="fty.txt", issue_number="FTY") == [
            Issue(
                column=1,
                line=1,
                issue_number="FTY001",
                message=(
                    "guard import by `if False:  # TYPE_CHECKING`: Type (not in 3.5.0, 3.5.1) "
                    "(originally reported as TYP001)"
                ),
            )
        ]

    @pytest.mark.parametrize("is_default,expected", [(True, "3.8.0"), (False, "3.5.0")])
    def test_pre_parse_options(
        self, mocker: MockerFixture, is_default: bool, expected: str
    ) -> None:
        options = mocker.Mock(spec=AbstractNamespace)
        options.ftp_is_default.return_value = is_default
        options.min_python_version = "3.5.0"
        options.python_version = "3.8.0"

        TypingImportChecker.pre_parse_options(options)

        assert options.python_version == "3.8.0"
        assert options.min_python_version == expected

    def test_pre_parse_options_not_supported(self, mocker: MockerFixture) -> None:
        options = mocker.Mock(spec=AbstractNamespace)
        options.ftp_is_default.return_value = True
        options.min_python_version = "3.5.0"
        options.python_version = "3.9.50"

        TypingImportChecker.pre_parse_options(options)

        assert options.python_version == "3.9.50"
        assert options.min_python_version == "3.9.20"

    def test_pre_parse_options_unknown(self, mocker: MockerFixture) -> None:
        options = mocker.Mock(spec=AbstractNamespace)
        options.ftp_is_default.return_value = True
        options.min_python_version = "3.5.0"
        options.python_version = "0.0.0"

        TypingImportChecker.pre_parse_options(options)

        assert options.python_version == "0.0.0"
        assert options.min_python_version == "0.0.0"
