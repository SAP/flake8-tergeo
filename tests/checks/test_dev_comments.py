"""Tests for _flake8_tergeo.dev_comments."""

from __future__ import annotations

from functools import partial

from pytest_mock import MockerFixture

from _flake8_tergeo import Issue, dev_comments
from tests.conftest import Flake8RunnerFixture

_FTP010 = partial(
    Issue,
    issue_number="FTP010",
    message="Usage of disallowed dev comment identifier '{identifier}'.",
)
FTP011 = partial(
    Issue,
    issue_number="FTP011",
    message="Missing tracking id in dev comment.",
)
_FTP012 = partial(
    Issue,
    issue_number="FTP012",
    message="Invalid tracking id '{ticket_id}' in dev comment.",
)
FTP013 = partial(
    Issue,
    issue_number="FTP013",
    message="Missing description in dev comment.",
)


def FTP010(  # pylint:disable=invalid-name
    *, line: int, column: int, identifier: str
) -> Issue:
    issue = _FTP010(line=line, column=column)
    return issue._replace(message=issue.message.format(identifier=identifier))


def FTP012(  # pylint:disable=invalid-name
    *, line: int, column: int, ticket_id: str
) -> Issue:
    issue = _FTP012(line=line, column=column)
    return issue._replace(message=issue.message.format(ticket_id=ticket_id))


class TestFTP010:
    def test_ftp010_no_config(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp010.txt", issue_number="FTP010")

    def test_ftp010(self, runner: Flake8RunnerFixture) -> None:
        results = runner(
            filename="ftp010.txt",
            issue_number="FTP010",
            args=("--ftp-dev-comments-disallowed-synonyms", "XXX"),
        )
        assert results == [
            FTP010(line=5, column=1, identifier="XXX"),
            FTP010(line=6, column=1, identifier="XXX"),
        ]


class TestFTP011:
    def test_ftp011_no_config(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp011.txt", issue_number="FTP011")

    def test_ftp011(self, runner: Flake8RunnerFixture) -> None:
        results = runner(
            filename="ftp011.txt",
            issue_number="FTP011",
            args=("--ftp-dev-comments-tracking-project-ids", "PRO"),
        )
        assert results == [FTP011(line=5, column=1)]


class TestFTP012:
    def test_ftp012_no_config(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp012.txt", issue_number="FTP012")

    def test_ftp012(self, runner: Flake8RunnerFixture) -> None:
        results = runner(
            filename="ftp012.txt",
            issue_number="FTP012",
            args=("--ftp-dev-comments-tracking-project-ids", "PRO"),
        )
        assert results == [
            FTP012(line=8, column=1, ticket_id="XXX"),
            FTP012(line=9, column=1, ticket_id="XXX-22"),
            FTP012(line=10, column=1, ticket_id="PRO"),
        ]


class TestFTP013:
    def test_ftp013_no_config(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp013.txt", issue_number="FTP013")

    def test_ftp013(self, runner: Flake8RunnerFixture) -> None:
        results = runner(
            filename="ftp013.txt",
            issue_number="FTP013",
            args=("--ftp-dev-comments-enforce-description",),
        )
        assert results == [FTP013(line=4, column=1)]


def test_add_options(mocker: MockerFixture) -> None:
    option_manager = mocker.Mock()
    dev_comments.add_options(option_manager)

    assert option_manager.add_option.call_args_list == [
        mocker.call(
            "--dev-comments-tracking-project-ids",
            parse_from_config=True,
            comma_separated_list=True,
            default=[],
        ),
        mocker.call(
            "--dev-comments-allowed-synonyms",
            parse_from_config=True,
            comma_separated_list=True,
            default=["TODO"],
        ),
        mocker.call(
            "--dev-comments-disallowed-synonyms",
            parse_from_config=True,
            comma_separated_list=True,
            default=["FIXME"],
        ),
        mocker.call(
            "--dev-comments-enforce-description",
            parse_from_config=True,
            action="store_true",
        ),
    ]


def test_parse_options(mocker: MockerFixture) -> None:
    options = mocker.Mock()
    options.dev_comments_tracking_project_ids = ["p1"]
    options.dev_comments_allowed_synonyms = ["a1", "A2"]
    options.dev_comments_disallowed_synonyms = ["D1", "d2"]
    options.dev_comments_enforce_description = True

    dev_comments.parse_options(options)
    assert options.dev_comments_tracking_project_ids == ["p1"]
    assert options.dev_comments_allowed_synonyms == ["A1", "A2"]
    assert options.dev_comments_disallowed_synonyms == ["D1", "D2"]
    assert options.dev_comments_enforce_description
    assert options.dev_comments_tracking_regex.pattern == r"(P1-[0-9]+)"
