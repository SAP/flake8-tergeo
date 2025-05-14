"""Tests for _flake8_tergeo.checks.requirements"""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
from argparse import Namespace
from collections.abc import Iterator
from functools import partial
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from _flake8_tergeo import base
from _flake8_tergeo.ast_util import set_info_in_tree
from _flake8_tergeo.checks import requirements
from _flake8_tergeo.flake8_types import Issue
from tests.conftest import Flake8RunnerFixture
from tests.path_util import mkdir, mkfile


@pytest.fixture(scope="session")
def project_names() -> dict[str, str]:
    unique = os.getenv("PYTEST_XDIST_WORKER", "main")
    return {
        "project1": f"project1_{unique}",
        "project2": f"project2_{unique}",
        "project3": f"project3_{unique}",
        "root": f"root_{unique}",
    }


@pytest.fixture
def args(project_names: dict[str, str]) -> tuple[str, ...]:
    return (
        "--ftp-distribution-name",
        project_names["root"],
        "--ftp-requirements-mapping",
        (
            f"foo:{project_names['project1']},"
            f"ns.a:{project_names['project2']},"
            f"ns.b:{project_names['project3']}"
        ),
        "--ftp-requirements-packages",
        "root_additional",
        "--ftp-requirements-ignore-type-checking-block",
    )


@pytest.fixture
def args_with_extra_mapping(tmp_path: Path, args: tuple[str, ...]) -> tuple[str, ...]:
    base_path = str(tmp_path).replace("/", ".")
    if base_path.startswith("."):
        base_path = base_path[1:]

    return (
        *args,
        "--ftp-requirements-module-extra-mapping",
        f"{base_path}.project.dev | dev, {base_path}.project.main::doit | doc",
    )


@pytest.fixture
def options() -> Namespace:
    return Namespace(
        requirements_mapping=None,
        requirements_packages=[],
        distribution_name="foo",
        requirements_module_extra_mapping={},
        requirements_ignore_type_checking_block=False,
    )


_FTP041 = partial(
    Issue,
    issue_number="FTP041",
    message="Found illegal import of {module}. It is not part of the projects requirements",
)

_FTP041_EXTRAS = partial(
    Issue,
    issue_number="FTP041",
    message=(
        "Found illegal import of {module}. The imported module is part of the projects "
        "requirements but the current module/package cannot use anything "
        "from the extra requirement(s) {extras}"
    ),
)


def FTP041(  # pylint:disable=invalid-name
    *, line: int, column: int, module: str, extras: str | None = None
) -> Issue:
    issue_partial = _FTP041 if not extras else _FTP041_EXTRAS
    issue = issue_partial(line=line, column=column)
    return issue._replace(message=issue.message.format(module=module, extras=extras))


def _create_project(
    name: str, filename: str, tmp_path: Path, datadir: Path, **kwargs: Any
) -> None:
    project = mkdir(tmp_path, name)

    # copy and adjust the pyproject.toml
    pyproject = project / "pyproject.toml"
    shutil.copyfile(datadir / filename, pyproject)
    content = pyproject.read_text(encoding="utf-8")
    content = content.format(name=name, **kwargs)
    pyproject.write_text(content, encoding="utf-8")

    # create a dummy package
    package = mkdir(project, name)
    mkfile(package, "__init__.py")

    # install the package in the current venv
    subprocess.run(
        ["pip", "install", "--no-deps", "--no-cache-dir", "-e", project], check=True
    )


def _remove_package(project: str) -> None:
    subprocess.run(["pip", "uninstall", "--yes", project], check=True)


def _find_import_node(code: str) -> ast.Import | ast.ImportFrom:
    tree = ast.parse(code)
    set_info_in_tree(tree)

    found = _find_import_node_recursive(tree)
    if not found:
        pytest.fail("Invalid code sample")
    return found


def _find_import_node_recursive(node: ast.AST) -> ast.Import | ast.ImportFrom | None:
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.Import, ast.ImportFrom)):
            return child
        found = _find_import_node_recursive(child)
        if found:
            return found
    return None


@pytest.fixture(scope="session")
def create_dummy_packages(
    tmp_path_factory: pytest.TempPathFactory, project_names: dict[str, str]
) -> Iterator[None]:
    tmp_path = tmp_path_factory.mktemp("packages")
    datadir = Path(__file__).parent / Path(__file__).stem

    _create_project(project_names["project1"], "base_pyproject.txt", tmp_path, datadir)
    _create_project(project_names["project2"], "base_pyproject.txt", tmp_path, datadir)
    _create_project(project_names["project3"], "base_pyproject.txt", tmp_path, datadir)
    _create_project(
        project_names["root"],
        "root_pyproject.txt",
        tmp_path,
        datadir,
        p1=project_names["project1"],
        p2=project_names["project2"],
        p3=project_names["project3"],
    )

    yield

    for project in project_names.values():
        _remove_package(project)


def test_add_options(mocker: MockerFixture) -> None:
    option_manager = mocker.Mock()
    requirements.add_options(option_manager)

    assert option_manager.add_option.call_args_list == [
        mocker.call("--distribution-name", parse_from_config=True, default=None),
        mocker.call("--requirements-mapping", parse_from_config=True, default=None),
        mocker.call(
            "--requirements-module-extra-mapping", parse_from_config=True, default=None
        ),
        mocker.call(
            "--requirements-packages",
            parse_from_config=True,
            comma_separated_list=True,
            default=[],
        ),
        mocker.call(
            "--requirements-ignore-type-checking-block",
            parse_from_config=True,
            action="store_true",
        ),
    ]


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, {}),
        ("", {}),
        ("foo:bar", {"foo": "bar"}),
        ("foo.baz:bar", {"foo.baz": "bar"}),
        ("foo:bar,", {"foo": "bar"}),
        ("foo:bar,a:b", {"foo": "bar", "a": "b"}),
        ("\nfoo:bar,\na:b", {"foo": "bar", "a": "b"}),
    ],
)
def test_parse_options_requirements_mapping(
    mocker: MockerFixture,
    value: str | None,
    expected: dict[str, str],
    options: Namespace,
) -> None:
    mocker.patch.object(requirements, "_requires", return_value=["bar", "baz"])

    options.requirements_mapping = value

    requirements.parse_options(options)
    assert options.requirements_mapping == expected  # type:ignore[comparison-overlap]


def test_parse_options_unknown_package(options: Namespace) -> None:
    with pytest.raises(PackageNotFoundError):
        requirements.parse_options(options)


def test_parse_options_no_requires_list(
    mocker: MockerFixture, options: Namespace
) -> None:
    mocker.patch.object(requirements, "_base_requires", return_value=None)

    with pytest.raises(PackageNotFoundError):
        requirements.parse_options(options)


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, {}),
        ("", {}),
        ("foo | *", {("foo", None): ["*"]}),
        (",foo | *", {("foo", None): ["*"]}),
        ("foo | a b", {("foo", None): ["a", "b"]}),
        ("foo | a-b", {("foo", None): ["a-b"]}),
        ("foo.bar | x", {("foo.bar", None): ["x"]}),
        ("foo.bar::X | x", {("foo.bar", "X"): ["x"]}),
        ("foo.bar::X::bar | a b", {("foo.bar", "X::bar"): ["a", "b"]}),
        ("foo | *,\nbar  |  a b", {("foo", None): ["*"], ("bar", None): ["a", "b"]}),
    ],
)
def test_parse_module_extra_mapping(
    mocker: MockerFixture,
    value: str | None,
    expected: dict[tuple[str, str], str],
    options: Namespace,
) -> None:
    mocker.patch.object(requirements, "_requires", return_value=["bar", "baz"])
    options.requirements_module_extra_mapping = value
    requirements.parse_options(options)

    assert (
        options.requirements_module_extra_mapping  # type:ignore[comparison-overlap]
        == expected
    )


def test_parse_options(mocker: MockerFixture, options: Namespace) -> None:
    mocker.patch.object(
        requirements,
        "_requires",
        return_value=[
            "dep-1==1.2.3",
            'dep.2~=4.5; python_version < "3.11"',
            "dep-3>=4; extra == 'testing'",
            'dep_4==0.8.0; python_version < "3.10" and extra == "flake8"',
        ],
    )
    mocker.patch.object(requirements, "stdlib_module_names", ["std1", "std2"])

    options.requirements_mapping = "foo:bar"
    options.requirements_packages = ["a", "b"]

    requirements.parse_options(options)
    assert options.requirements_mapping == {  # type:ignore[comparison-overlap]
        "foo": "bar"
    }
    assert options.distribution_name == "foo"
    assert options.requirements_packages == ["a", "b"]
    assert options.requirements_allow_list == {
        "": ["dep_1", "dep_2", "std1", "std2", "a", "b"],
        "testing": ["dep_3"],
        "flake8": ["dep_4"],
    }
    assert not options.requirements_ignore_type_checking_block
    assert options.requirements_module_extra_mapping == {}


def test_parse_options_without_distribution_name(options: Namespace) -> None:
    options.distribution_name = None

    requirements.parse_options(options)
    assert not options.distribution_name


@pytest.mark.parametrize(
    "name,expected",
    [
        ("foo", "foo"),
        ("some_package", "some_package"),
        ("some-package", "some_package"),
    ],
)
def test_normalize(name: str, expected: str) -> None:
    assert requirements._normalize(name) == expected


@pytest.mark.parametrize("ignore_type_checking_block", [True, False])
@pytest.mark.parametrize(
    "code,ignore", [("import x", False), ("if TYPE_CHECKING: import foo", True)]
)
def test_ignore_import(
    code: str, ignore: bool, ignore_type_checking_block: bool
) -> None:
    options = requirements._Options(
        requirements_ignore_type_checking_block=ignore_type_checking_block
    )
    node = _find_import_node(code)

    result = requirements._ignore_import(options, node)
    if ignore_type_checking_block:
        assert result == ignore
    else:
        assert result is False


def test_get_module_name(mocker: MockerFixture, tmp_path: Path) -> None:
    get_plugin = mocker.patch.object(base, "get_plugin")

    main_dir = mkdir(tmp_path, "main")
    inner_dir = mkdir(main_dir, "inner")
    file1 = mkfile(inner_dir, "foo.py").relative_to(tmp_path)
    file2 = mkfile(inner_dir, "__init__.py").relative_to(tmp_path)
    file3 = mkfile(main_dir, "some.py").relative_to(tmp_path)

    get_plugin().filename = str(file1)
    assert requirements._get_module_name() == "main.inner.foo"
    get_plugin().filename = str(file2)
    assert requirements._get_module_name() == "main.inner"
    get_plugin().filename = str(file3)
    assert requirements._get_module_name() == "main.some"


@pytest.mark.parametrize(
    "value,sep,expected",
    [
        ("foo", ":", ["foo"]),
        ("foo:bar", ":", ["foo", "foo:bar"]),
        ("a.b.c", ".", ["a", "a.b", "a.b.c"]),
    ],
)
def test_build_combinations(value: str, sep: str, expected: list[str]) -> None:
    assert requirements._build_combinations(value, sep) == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        ("import foo", ""),
        ("def func(): import foo", "func"),
        ("class A:\n  def func(): import foo", "A::func"),
        ("def outer():\n  def func(): import foo", "outer::func"),
    ],
)
def test_get_identifier(code: str, expected: str) -> None:
    node = _find_import_node(code)
    assert requirements._get_identifier(node) == expected


@pytest.mark.usefixtures("create_dummy_packages")
def test_ftp041_ignore(runner: Flake8RunnerFixture, args: tuple[str, ...]) -> None:
    assert not runner(filename="ftp041_ignore.txt", issue_number="FTP041", args=args)


@pytest.mark.usefixtures("create_dummy_packages")
def test_ftp041_no_config(runner: Flake8RunnerFixture) -> None:
    assert not runner(filename="ftp041_ignore.txt", issue_number="FTP041")


@pytest.mark.parametrize(
    "imp,module",
    [
        ("import x", "x"),
        ("import x.y", "x.y"),
        ("import foo, x", "x"),
        ("from x import x", "x.x"),
        ("from x.y import z", "x.y.z"),
        # namespace package checks
        ("from ns.c import foo", "ns.c.foo"),
        ("import ns.c.baz", "ns.c.baz"),
    ],
)
@pytest.mark.usefixtures("create_dummy_packages")
def test_ftp041(
    runner: Flake8RunnerFixture, imp: str, module: str, args: tuple[str, ...]
) -> None:
    results = runner(filename="ftp041.txt", issue_number="FTP041", imp=imp, args=args)
    assert results == [FTP041(line=1, column=1, module=module)]


@pytest.mark.parametrize(
    "imp,filename",
    [
        ("import foo", "project/main/__init__.txt"),
        ("def doit(): import ns.b", "project/main/__init__.txt"),
        ("import ns.a", "project/dev/dev.txt"),
        ("import ns.a", "project/dev/sub/__init__.txt"),
    ],
)
@pytest.mark.usefixtures("create_dummy_packages")
def test_ftp041_extra_mapping_ignore(
    runner: Flake8RunnerFixture,
    imp: str,
    filename: str,
    args_with_extra_mapping: tuple[str, ...],
) -> None:
    assert not runner(
        filename=filename, issue_number="FTP041", imp=imp, args=args_with_extra_mapping
    )


@pytest.mark.parametrize(
    "filename,imp,module,column,extras",
    [
        # main can only use install requirements
        ("project/main/__init__.txt", "import x", "x", 1, None),
        ("project/main/__init__.txt", "import ns.a", "ns.a", 1, "dev"),
        ("project/main/__init__.txt", "def foo(): import ns.a", "ns.a", 12, "dev"),
        # main::doit can only use install/doc requirements
        ("project/main/__init__.txt", "def doit(): import x", "x", 13, None),
        ("project/main/__init__.txt", "def doit(): import ns.a", "ns.a", 13, "dev"),
        # also submodules are checked properly
        ("project/main/mod.txt", "import x", "x", 1, None),
        ("project/main/mod.txt", "import ns.a", "ns.a", 1, "dev"),
        # dev can only use dev requirements
        ("project/dev/dev.txt", "import x", "x", 1, None),
        ("project/dev/dev.txt", "import ns.b", "ns.b", 1, "doc"),
        ("project/dev/dev.txt", "def foo(): import ns.b", "ns.b", 12, "doc"),
        # dev submodules can only use dev requirements
        ("project/dev/sub/__init__.txt", "import x", "x", 1, None),
        ("project/dev/sub/__init__.txt", "import ns.b", "ns.b", 1, "doc"),
    ],
)
@pytest.mark.usefixtures("create_dummy_packages")
def test_ftp041_extra_mapping(
    runner: Flake8RunnerFixture,
    imp: str,
    module: str,
    filename: str,
    extras: str | None,
    column: int,
    args_with_extra_mapping: tuple[str, ...],
) -> None:
    results = runner(
        filename=filename,
        issue_number="FTP041",
        imp=imp,
        args=args_with_extra_mapping,
    )
    assert results == [FTP041(line=1, column=column, module=module, extras=extras)]
