"""Tests for _flake8_tergeo.checks.parens."""

from __future__ import annotations

from functools import partial

import pytest
from pytest_mock import MockerFixture

from _flake8_tergeo import Issue, parens
from tests.conftest import Flake8RunnerFixture

FTP008 = partial(Issue, issue_number="FTP008", message="Found unnecessary parenthesis.")


@pytest.mark.parametrize("disallow_single_tuple", [True, False])
def test_ftp008(runner: Flake8RunnerFixture, disallow_single_tuple: bool) -> None:
    results = runner(
        filename="ftp008.txt",
        issue_number="FTP008",
        args=(
            ("--ftp-disallow-parens-in-return-single-element-tuple",)
            if disallow_single_tuple
            else ()
        ),
    )
    assert results == [
        FTP008(line=51, column=7),
        FTP008(line=52, column=7),
        FTP008(line=53, column=7),
        FTP008(line=55, column=5),
        FTP008(line=58, column=5),
        FTP008(line=63, column=13),
        FTP008(line=65, column=12),
        FTP008(line=67, column=12),
        FTP008(line=69, column=12),
        FTP008(line=71, column=12),
        FTP008(line=73, column=12),
    ]


@pytest.mark.parametrize("disallow_single_tuple", [True, False])
def test_ftp008_single_element_tuple(
    runner: Flake8RunnerFixture, disallow_single_tuple: bool
) -> None:
    results = runner(
        filename="ftp008_single_element_tuple.txt",
        issue_number="FTP008",
        args=(
            ("--ftp-disallow-parens-in-return-single-element-tuple",)
            if disallow_single_tuple
            else ()
        ),
    )
    if disallow_single_tuple:
        assert results == [
            FTP008(line=2, column=12),
            FTP008(line=4, column=12),
            FTP008(line=6, column=18),
        ]
    else:
        assert results == []


def test_add_options(mocker: MockerFixture) -> None:
    option_manager = mocker.Mock()
    parens.add_options(option_manager)

    assert option_manager.add_option.call_args_list == [
        mocker.call(
            "--disallow-parens-in-return-single-element-tuple",
            parse_from_config=True,
            action="store_true",
        ),
    ]
