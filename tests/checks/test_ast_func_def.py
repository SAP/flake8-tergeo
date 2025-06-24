"""Tests for _flake8_tergeo.checks.ast_func_def."""

from __future__ import annotations

from functools import partial

import pytest
from dirty_equals import IsOneOf
from pytest_mock import MockerFixture

from _flake8_tergeo import Issue, ast_func_def
from tests.conftest import Flake8RunnerFixture
from tests.util import LenientIssue

ignore_parameters = pytest.mark.parametrize("ignore_ann_assign", [True, False])


_FTP042 = partial(
    Issue,
    issue_number="FTP042",
    message="The magic method {func} is no longer used in python3 "
    "and should be removed.",
)
_FTP043 = partial(
    Issue,
    issue_number="FTP043",
    message="The function {func} implies a return but it returns/yields nothing.",
)
FTP071 = partial(
    Issue,
    issue_number="FTP071",
    message="Found assign and return. Remove the assignment and return directly.",
)
_FTP093 = partial(
    Issue,
    issue_number="FTP093",
    message=(
        "The function {func} implies a boolean return type but it returns something else."
    ),
)
_FTP096 = partial(
    LenientIssue,
    issue_number="FTP096",
    message="Found descriptor {descriptor} on function outside a class.",
)
FTP122 = partial(
    Issue,
    issue_number="FTP122",
    message="The behavior of a classmethod and property decorator is unreliable. "
    "Avoid defining class properties.",
)
FTP107 = partial(
    Issue,
    issue_number="FTP107",
    message="Instead of using typing.Never for return annotations, use typing.NoReturn.",
)
FTP125 = partial(
    Issue,
    issue_number="FTP125",
    message="The override decorator should be the first decorator or "
    "if present placed directly below descriptor based decorators.",
)


def FTP042(  # pylint:disable=invalid-name
    *, line: int, column: int, func: str
) -> Issue:
    issue = _FTP042(line=line, column=column)
    return issue._replace(message=issue.message.format(func=func))


def FTP043(  # pylint:disable=invalid-name
    *, line: int, column: int, func: str
) -> Issue:
    issue = _FTP043(line=line, column=column)
    return issue._replace(message=issue.message.format(func=func))


def FTP093(  # pylint:disable=invalid-name
    *, line: int, column: int, func: str
) -> Issue:
    issue = _FTP093(line=line, column=column)
    return issue._replace(message=issue.message.format(func=func))


def FTP096(  # pylint:disable=invalid-name
    *, line: int | IsOneOf, column: int, descriptor: str
) -> LenientIssue:
    issue = _FTP096(line=line, column=column)
    return issue._replace(message=issue.message.format(descriptor=descriptor))


@ignore_parameters
def test_ftp071(runner: Flake8RunnerFixture, ignore_ann_assign: bool) -> None:
    results = runner(
        filename="ftp071.txt",
        issue_number="FTP071",
        args=("--ftp-ignore-annotation-in-assign-return",) if ignore_ann_assign else (),
    )
    assert results == [
        FTP071(line=47, column=5),
        FTP071(line=51, column=5),
        FTP071(line=55, column=9),
        *([] if ignore_ann_assign else [FTP071(line=62, column=5)]),
        FTP071(line=67, column=13),
        FTP071(line=74, column=13),
        FTP071(line=81, column=13),
    ]


@pytest.mark.parametrize("cls_name", ["TypeGuard", "TypeIs"])
@pytest.mark.parametrize(
    "imp,cls",
    [
        ("import typing", "typing.{cls_name}"),
        ("from typing import {cls_name}", "{cls_name}"),
        ("import typing_extensions", "typing_extensions.{cls_name}"),
        ("from typing_extensions import {cls_name}", "{cls_name}"),
    ],
)
def test_ftp093(runner: Flake8RunnerFixture, cls_name: str, imp: str, cls: str) -> None:
    results = runner(
        filename="ftp093.txt",
        issue_number="FTP093",
        imp=imp.format(cls_name=cls_name),
        cls=cls.format(cls_name=cls_name),
    )
    assert results == [
        FTP093(line=18, column=1, func="is_foo"),
        FTP093(line=19, column=1, func="Is_foo"),
        FTP093(line=20, column=1, func="Is_foo"),
        FTP093(line=21, column=1, func="Is_foo"),
        FTP093(line=22, column=1, func="is_foo"),
        FTP093(line=23, column=1, func="Have_foo"),
        FTP093(line=24, column=1, func="has_foo"),
        FTP093(line=25, column=1, func="can_foo"),
        FTP093(line=26, column=1, func="_can_foo"),
        FTP093(line=27, column=1, func="__can_foo__"),
    ]


def test_ftp043(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp043.txt", issue_number="FTP043")
    assert results == [
        FTP043(line=40, column=1, func="get_foo"),
        FTP043(line=41, column=1, func="get__bar"),
        FTP043(line=42, column=1, func="get_bar"),
        FTP043(line=43, column=1, func="_get_foo"),
        FTP043(line=44, column=1, func="__get_foo__"),
    ]


@pytest.mark.parametrize("func", ast_func_def.PY2_REMOVED_METHODS)
def test_ftp042(runner: Flake8RunnerFixture, func: str) -> None:
    results = runner(filename="ftp042.txt", issue_number="FTP042", func=func)
    assert results == [FTP042(line=9, column=5, func=func)]


@pytest.mark.parametrize("descriptor", ast_func_def.DESCRIPTORS)
def test_ftp096(runner: Flake8RunnerFixture, descriptor: str) -> None:
    results = runner(
        filename="ftp096.txt", issue_number="FTP096", descriptor=descriptor
    )
    assert results == [
        FTP096(line=IsOneOf(18, 19), column=1, descriptor=descriptor),
        FTP096(line=IsOneOf(23, 24), column=9, descriptor=descriptor),
    ]


def test_add_options(mocker: MockerFixture) -> None:
    option_manager = mocker.Mock()
    ast_func_def.add_options(option_manager)

    assert option_manager.add_option.call_args_list == [
        mocker.call(
            "--ignore-annotation-in-assign-return",
            parse_from_config=True,
            action="store_true",
        ),
    ]


def test_ftp122(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp122.txt", issue_number="FTP122")
    assert results == [FTP122(line=15, column=5)]


class TestFTP107:
    @pytest.mark.parametrize(
        "imp,never",
        [
            ("import foo", "foo.Never"),
            ("from foo import Never", "Never"),
            ("from foo import typing", "typing.Never"),
        ],
    )
    def test_ignore(self, runner: Flake8RunnerFixture, imp: str, never: str) -> None:
        assert not runner(
            filename="ftp107.txt", issue_number="FTP107", imp=imp, never=never
        )

    @pytest.mark.parametrize(
        "imp,never",
        [
            ("from typing import Never", "Never"),
            ("import typing", "typing.Never"),
        ],
    )
    def test(self, runner: Flake8RunnerFixture, imp: str, never: str) -> None:
        results = runner(
            filename="ftp107.txt", issue_number="FTP107", imp=imp, never=never
        )
        assert results == [FTP107(line=11, column=14)]


class TestFTP125:
    @pytest.mark.parametrize(
        "imp,override",
        [
            ("import foo", "foo.override"),
            ("from foo import override", "override"),
            ("from foo import override", "typing.override"),
        ],
    )
    def test_ignore(self, runner: Flake8RunnerFixture, imp: str, override: str) -> None:
        assert not runner(
            filename="ftp125.txt", issue_number="FTP125", imp=imp, override=override
        )

    @pytest.mark.parametrize(
        "imp,override",
        [
            ("from typing import override", "override"),
            ("import typing", "typing.override"),
        ],
    )
    def test(self, runner: Flake8RunnerFixture, imp: str, override: str) -> None:
        results = runner(
            filename="ftp125.txt", issue_number="FTP125", imp=imp, override=override
        )
        assert results == [
            FTP125(line=27, column=2),
            FTP125(line=30, column=2),
            FTP125(line=35, column=2),
        ]
