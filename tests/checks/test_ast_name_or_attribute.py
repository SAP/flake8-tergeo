"""Tests for _flake8_tergeo.checks.ast_name_or_attribute."""

from __future__ import annotations

from functools import partial

import pytest

from _flake8_tergeo import Issue, ast_name_or_attribute
from _flake8_tergeo.checks.ast_name_or_attribute import OS_DEPENDENT_PATH
from tests.conftest import Flake8RunnerFixture

FTP099 = partial(
    Issue,
    issue_number="FTP099",
    message="Use datetime.UTC instead of datetime.timezone.utc.",
)
FTP220 = partial(
    Issue,
    issue_number="FTP220",
    message="Use http.HTTPStatus instead of requests.codes.",
)
FTP064 = partial(
    Issue,
    issue_number="FTP064",
    message="Found use of __debug__.",
)
FTP016 = partial(
    Issue,
    issue_number="FTP016",
    message="Found use of __metaclass__. Use metaclass= in the class signature",
)
FTP076 = partial(
    Issue,
    issue_number="FTP076",
    message="Found usage/import of re.DEBUG.",
)
FTP054 = partial(Issue, issue_number="FTP054", message="Use PEP 604 syntax for unions.")
FTP055 = partial(
    Issue,
    issue_number="FTP055",
    message="Use PEP 604 syntax for Optional[X] like 'X|None'.",
)
_FTP056 = partial(
    Issue,
    issue_number="FTP056",
    message="Use builtin {instead} instead of {original}.",
)
_FTP089 = partial(
    Issue,
    issue_number="FTP089",
    message="Found OSError alias {alias}; use OSError instead.",
)
FTP039 = partial(
    Issue, issue_number="FTP039", message="Found dunder in the middle of a name."
)
FTP103 = partial(
    Issue,
    issue_number="FTP103",
    message="Use the OS independent classes pathlib.Path or pathlib.PurePath instead of OS "
    "dependent ones.",
)
FTP105 = partial(
    Issue,
    issue_number="FTP105",
    message="Found nested union. Use a single Union instead.",
)
FTP108 = partial(
    Issue,
    issue_number="FTP108",
    message="Instead of using typing.NoReturn for annotations, use typing.Never.",
)
FTP003 = partial(
    Issue,
    issue_number="FTP003",
    message=(
        "Found usage/import of datetime.utcnow. Consider to use datetime.now(tz=)."
    ),
)
FTP007 = partial(
    Issue,
    issue_number="FTP007",
    message=(
        "Found usage/import of datetime.utcfromtimestamp. "
        "Consider to use datetime.fromtimestamp(tz=)."
    ),
)


def FTP056(  # pylint: disable=invalid-name
    *, line: int, column: int, builtin: str
) -> Issue:
    issue = _FTP056(line=line, column=column)
    builtin = builtin.replace("typing.", "")
    return issue._replace(
        message=issue.message.format(instead=builtin.lower(), original=builtin)
    )


def FTP089(  # pylint: disable=invalid-name
    *, line: int, column: int, alias: str
) -> Issue:
    issue = _FTP089(line=line, column=column)
    return issue._replace(message=issue.message.format(alias=alias))


def test_ftp089(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp089.txt", issue_number="FTP089")
    assert results == [
        FTP089(line=6, column=1, alias="EnvironmentError"),
        FTP089(line=7, column=1, alias="IOError"),
        FTP089(line=8, column=1, alias="WindowsError"),
    ]


def test_ftp064(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp064.txt", issue_number="FTP064")
    assert results == [FTP064(line=8, column=1)]


def test_ftp016(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp016.txt", issue_number="FTP016")
    assert results == [FTP016(line=8, column=1)]


class TestFTP076:
    def test_ftp076_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp076.txt", issue_number="FTP076")

    @pytest.mark.parametrize(
        "imp,name", [("import re", "re.DEBUG"), ("from re import DEBUG", "DEBUG")]
    )
    def test_ftp076(self, runner: Flake8RunnerFixture, imp: str, name: str) -> None:
        results = runner(
            filename="ftp076.txt", issue_number="FTP076", imp=imp, name=name
        )
        assert results == [FTP076(line=3, column=1)]


@pytest.mark.parametrize(
    "future,find_by_future",
    [
        ("from __future__ import annotations", True),
        ("from foo import annotations", False),
    ],
)
@pytest.mark.parametrize(
    "imp,find_by_imp,union",
    [
        ("from typing import Union", True, "Union"),
        ("import typing", True, "typing.Union"),
        ("import foo", False, "foo.Union"),
        ("from foo import Union", False, "Union"),
        ("from foo import typing", False, "typing.Union"),
    ],
)
@pytest.mark.parametrize(
    "version,find_by_version", [("3.7.0", False), ("3.10.0", True)]
)
def test_ftp054(
    runner: Flake8RunnerFixture,
    future: str,
    find_by_future: bool,
    imp: str,
    find_by_imp: bool,
    union: str,
    version: str,
    find_by_version: bool,
) -> None:
    results = runner(
        filename="ftp054.txt",
        issue_number="FTP054",
        future=future,
        imp=imp,
        union=union,
        args=("--ftp-python-version", version),
    )
    if find_by_imp and (find_by_future or find_by_version):
        assert results == [
            FTP054(line=7, column=8),
            FTP054(line=8, column=9),
            FTP054(line=10, column=4),
            FTP054(line=11, column=14),
        ] + ([FTP054(line=13, column=5)] if find_by_version else [])
    elif find_by_imp:
        assert results == [FTP054(line=7, column=8), FTP054(line=8, column=9)]
    else:
        assert not results


@pytest.mark.parametrize(
    "future,find_by_future",
    [
        ("from __future__ import annotations", True),
        ("from foo import annotations", False),
    ],
)
@pytest.mark.parametrize(
    "imp,find_by_imp,optional",
    [
        ("from typing import Optional", True, "Optional"),
        ("import typing", True, "typing.Optional"),
        ("import foo", False, "foo.Optional"),
        ("from foo import Optional", False, "Optional"),
        ("from foo import typing", False, "typing.Optional"),
    ],
)
@pytest.mark.parametrize(
    "version,find_by_version", [("3.7.0", False), ("3.10.0", True)]
)
def test_ftp055(
    runner: Flake8RunnerFixture,
    future: str,
    find_by_future: bool,
    imp: str,
    find_by_imp: bool,
    optional: str,
    version: str,
    find_by_version: bool,
) -> None:
    results = runner(
        filename="ftp055.txt",
        issue_number="FTP055",
        future=future,
        imp=imp,
        optional=optional,
        args=("--ftp-python-version", version),
    )
    if find_by_imp and (find_by_future or find_by_version):
        assert results == [
            FTP055(line=7, column=8),
            FTP055(line=8, column=9),
            FTP055(line=10, column=4),
            FTP055(line=11, column=14),
        ] + ([FTP055(line=13, column=5)] if find_by_version else [])
    elif find_by_imp:
        assert results == [FTP055(line=7, column=8), FTP055(line=8, column=9)]
    else:
        assert not results


@pytest.mark.parametrize(
    "future,find_by_future",
    [
        ("from __future__ import annotations", True),
        ("from foo import annotations", False),
    ],
)
@pytest.mark.parametrize(
    "imp,find_by_imp,builtin",
    [
        ("import typing", True, f"typing.{builtin}")
        for builtin in ast_name_or_attribute.BUILTINS
    ]
    + [
        (f"from typing import {builtin}", True, builtin)
        for builtin in ast_name_or_attribute.BUILTINS
    ]
    + [
        ("import foo", False, "foo.Type"),
        ("from addict import Dict", False, "Dict"),
        ("import addict as typing", False, "typing.Dict"),
    ],
)
@pytest.mark.parametrize("version,find_by_version", [("3.8.0", False), ("3.9.0", True)])
def test_ftp056(
    runner: Flake8RunnerFixture,
    future: str,
    find_by_future: bool,
    imp: str,
    find_by_imp: bool,
    builtin: str,
    version: str,
    find_by_version: bool,
) -> None:
    results = runner(
        filename="ftp056.txt",
        issue_number="FTP056",
        future=future,
        imp=imp,
        builtin=builtin,
        args=("--ftp-python-version", version),
    )
    if find_by_imp and (find_by_future or find_by_version):
        assert results == [
            FTP056(line=7, column=8, builtin=builtin),
            FTP056(line=8, column=9, builtin=builtin),
            FTP056(line=10, column=4, builtin=builtin),
            FTP056(line=11, column=14, builtin=builtin),
        ] + ([FTP056(line=13, column=5, builtin=builtin)] if find_by_version else [])
    elif find_by_imp:
        assert results == [
            FTP056(line=7, column=8, builtin=builtin),
            FTP056(line=8, column=9, builtin=builtin),
        ]
    else:
        assert not results


class TestFTP099:
    params = pytest.mark.parametrize(
        "imp,utc",
        [
            ("import datetime", "datetime.timezone.utc"),
            ("from datetime import timezone", "timezone.utc"),
        ],
    )

    def test_ftp099_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(
            filename="ftp099_ignore.txt",
            issue_number="FTP099",
            args=("--ftp-python-version", "3.11.0"),
        )

    @params
    def test_ftp099_311(self, runner: Flake8RunnerFixture, imp: str, utc: str) -> None:
        results = runner(
            filename="ftp099.txt",
            issue_number="FTP099",
            args=("--ftp-python-version", "3.11.0"),
            imp=imp,
            utc=utc,
        )
        assert results == [FTP099(line=3, column=5), FTP099(line=4, column=5)]

    @params
    def test_ftp099_310(self, runner: Flake8RunnerFixture, imp: str, utc: str) -> None:
        assert not runner(
            filename="ftp099.txt",
            issue_number="FTP099",
            args=("--ftp-python-version", "3.10.0"),
            imp=imp,
            utc=utc,
        )


def test_ftp039(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp039.txt", issue_number="FTP039")
    assert results == [FTP039(line=7, column=1), FTP039(line=8, column=1)]


class TestFTP220:
    def test_ftp220_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp220_ignore.txt", issue_number="FTP220")

    @pytest.mark.parametrize(
        "imp,codes",
        [
            ("import requests", "requests.codes"),
            ("from requests import codes", "codes"),
            ("import requests.status_codes", "requests.status_codes.codes"),
            ("from requests import status_codes", "status_codes.codes"),
            ("from requests.status_codes import codes", "codes"),
        ],
    )
    def test_ftp220(self, runner: Flake8RunnerFixture, imp: str, codes: str) -> None:
        results = runner(
            filename="ftp220.txt", issue_number="FTP220", imp=imp, codes=codes
        )
        assert results == [FTP220(line=3, column=5)]


class TestFTP103:
    @pytest.mark.parametrize(
        "imp,path",
        [
            ("from foo import PureWindowsPath", "PureWindowsPath"),
            ("import pathlib", "pathlib.Path"),
            ("import pathlib", "pathlib.PurePath"),
            ("from pathlib import Path", "Path"),
            ("import bar", "bar.PosixPath"),
        ],
    )
    def test_ignore(self, runner: Flake8RunnerFixture, imp: str, path: str) -> None:
        assert not runner(
            filename="ftp103.txt", issue_number="FTP103", imp=imp, path=path
        )

    @pytest.mark.parametrize(
        "imp,path",
        [
            *[("import pathlib", f"pathlib.{path}") for path in OS_DEPENDENT_PATH],
            *[(f"from pathlib import {path}", path) for path in OS_DEPENDENT_PATH],
        ],
    )
    def test(self, runner: Flake8RunnerFixture, imp: str, path: str) -> None:
        results = runner(
            filename="ftp103.txt", issue_number="FTP103", imp=imp, path=path
        )
        assert results == [FTP103(line=10, column=1), FTP103(line=11, column=1)]


class TestFTP105:
    @pytest.mark.parametrize(
        "imp,union",
        [
            ("import foo", "foo.Union"),
            ("from foo import Union", "Union"),
            ("from foo import typing", "typing.Union"),
        ],
    )
    def test_ignore(self, runner: Flake8RunnerFixture, imp: str, union: str) -> None:
        assert not runner(
            filename="ftp105.txt", issue_number="FTP105", imp=imp, union=union
        )

    @pytest.mark.parametrize(
        "imp,union,col_offset",
        [
            ("from typing import Union", "Union", 0),
            ("import typing", "typing.Union", 7),
        ],
    )
    def test(
        self, runner: Flake8RunnerFixture, imp: str, union: str, col_offset: int
    ) -> None:
        results = runner(
            filename="ftp105.txt", issue_number="FTP105", imp=imp, union=union
        )
        assert results == [
            FTP105(line=12, column=11 + col_offset),
            FTP105(line=12, column=30 + col_offset * 2),
            FTP105(line=13, column=11 + col_offset),
        ]


class TestFTP108:
    @pytest.mark.parametrize(
        "imp,no_return",
        [
            ("import foo", "foo.NoReturn"),
            ("from foo import NoReturn", "NoReturn"),
            ("from foo import typing", "typing.NoReturn"),
        ],
    )
    def test_ignore(
        self, runner: Flake8RunnerFixture, imp: str, no_return: str
    ) -> None:
        assert not runner(
            filename="ftp108.txt", issue_number="FTP108", imp=imp, no_return=no_return
        )

    @pytest.mark.parametrize(
        "imp,no_return",
        [
            ("from typing import NoReturn", "NoReturn"),
            ("import typing", "typing.NoReturn"),
        ],
    )
    def test(self, runner: Flake8RunnerFixture, imp: str, no_return: str) -> None:
        results = runner(
            filename="ftp108.txt", issue_number="FTP108", imp=imp, no_return=no_return
        )
        assert results == [
            FTP108(line=10, column=20),
            FTP108(line=11, column=4),
        ]


class TestFTP003:
    def test_ftp003_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp003_ignore.txt", issue_number="FTP003")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("from datetime import datetime", "datetime.utcnow"),
            ("import datetime", "datetime.datetime.utcnow"),
            ("from datetime.datetime import utcnow", "utcnow"),
        ],
    )
    def test_ftp003(self, runner: Flake8RunnerFixture, imp: str, func: str) -> None:
        results = runner(
            filename="ftp003.txt", issue_number="FTP003", imp=imp, func=func
        )
        assert results == [FTP003(line=3, column=1)]


class TestFTP007:
    def test_ftp007_ignore(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(filename="ftp007_ignore.txt", issue_number="FTP007")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("from datetime import datetime", "datetime.utcfromtimestamp"),
            ("import datetime", "datetime.datetime.utcfromtimestamp"),
            ("from datetime.datetime import utcfromtimestamp", "utcfromtimestamp"),
        ],
    )
    def test_ftp007(self, runner: Flake8RunnerFixture, imp: str, func: str) -> None:
        results = runner(
            filename="ftp007.txt", issue_number="FTP007", imp=imp, func=func
        )
        assert results == [FTP007(line=3, column=1)]
