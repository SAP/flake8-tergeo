"""Tests for _flake8_tergeo.checks.filename."""

from __future__ import annotations

from functools import partial
from pathlib import Path

import pytest
from pytest_fixture_classes import fixture_class

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture
from tests.path_util import mkdir, mkfile

_FTP004 = partial(
    Issue, issue_number="FTP004", message="Name of {type_} '{name}' is invalid."
)
FTP020 = partial(Issue, issue_number="FTP020", message="Found encoding comment.")
FTP040 = partial(
    Issue,
    issue_number="FTP040",
    message="File is part of an implicit namespace package.",
)


def FTP004(  # pylint:disable=invalid-name
    *, line: int, column: int, type_: str, name: str
) -> Issue:
    issue = _FTP004(line=line, column=column)
    return issue._replace(message=issue.message.format(type_=type_, name=name))


@fixture_class(name="testfolder")
class TestFolderFixture:
    tmp_path: Path

    def __call__(self, foldername: str) -> Path:
        testdir = mkdir(self.tmp_path, foldername)
        mkfile(testdir, "__init__.py")
        mkfile(testdir, "foo.py")
        return testdir


class TestFTP020:
    def test_ftp020_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp020_ignore.txt", issue_number="FTP020")

    def test_ftp020(self, runner: Flake8RunnerFixture) -> None:
        results = runner(filename="ftp020.txt", issue_number="FTP020")
        assert results == [
            FTP020(line=1, column=1),
            FTP020(line=4, column=1),
            FTP020(line=7, column=1),
            FTP020(line=8, column=1),
        ]


class TestFTP004:
    @pytest.mark.parametrize(
        "filename", ["abc.py", "foo1.py", "foo_1.py", "abc_foo.py", "1_foo.py"]
    )
    def test_filename_ok(
        self, testfolder: TestFolderFixture, filename: str, runner: Flake8RunnerFixture
    ) -> None:
        path = mkfile(testfolder("foo"), filename)
        assert not runner(filename=str(path), issue_number="FTP004")

    @pytest.mark.parametrize("filename", ["Abc.py", ".foo.py", "foo-bar.py", "fooü.py"])
    def test_filename_not_ok(
        self, testfolder: TestFolderFixture, filename: str, runner: Flake8RunnerFixture
    ) -> None:
        path = mkfile(testfolder("foo"), filename)
        results = runner(filename=str(path), issue_number="FTP004")
        assert results == [FTP004(line=1, column=1, type_="file", name=filename[:-3])]

    @pytest.mark.parametrize("foldername", ["abc", "samples1", "foo_bar"])
    def test_foldername_ok(
        self,
        testfolder: TestFolderFixture,
        foldername: str,
        runner: Flake8RunnerFixture,
    ) -> None:
        path = testfolder(foldername) / "__init__.py"
        assert not runner(filename=str(path), issue_number="FTP004")

    @pytest.mark.parametrize("foldername", ["Abc", "föö", "foo-bar"])
    def test_foldername_not_ok(
        self,
        testfolder: TestFolderFixture,
        foldername: str,
        runner: Flake8RunnerFixture,
    ) -> None:
        path = testfolder(foldername) / "__init__.py"
        results = runner(filename=str(path), issue_number="FTP004")
        assert results == [FTP004(line=1, column=1, type_="package", name=foldername)]


class TestFTP040:
    def test_with_init_present(
        self, testfolder: TestFolderFixture, runner: Flake8RunnerFixture
    ) -> None:
        path = testfolder("foo") / "foo.py"
        assert not runner(filename=str(path), issue_number="FTP040")

    def test_fails_if_no_init(
        self, testfolder: TestFolderFixture, runner: Flake8RunnerFixture
    ) -> None:
        folder = mkdir(testfolder("foo"), "bar")
        file = mkfile(folder, "foo.py")
        results = runner(filename=str(file), issue_number="FTP040")
        assert results == [FTP040(line=1, column=1)]
