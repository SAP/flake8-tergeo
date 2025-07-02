"""Requirements checks."""

from __future__ import annotations

import ast
import functools
import re
from argparse import Namespace
from collections import defaultdict
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError
from importlib.metadata import requires as _base_requires
from pathlib import Path
from typing import NamedTuple, cast

import dependency_groups
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from _flake8_tergeo import base
from _flake8_tergeo.ast_util import get_parents
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.registry import (
    register,
    register_add_options,
    register_parse_options,
)
from _flake8_tergeo.util import stdlib_module_names

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type:ignore[import-not-found,no-redef]

EXTRA_PATTERN = re.compile(r'.*extra == "(?P<extra>[a-zA-Z0-9\-]+)".*')
INSTALL_REQUIRE_EXTRA = ""  # install requires have no real name, so use an empty string


class _Location(NamedTuple):
    module: str
    identifier: str | None


class _Options(Namespace):
    requirements_mapping: dict[str, str]
    distribution_name: str | None
    requirements_module_extra_mapping: dict[_Location, list[str]]
    requirements_ignore_type_checking_block: bool
    requirements_packages: list[str]
    requirements_allow_list: dict[str, list[str]]


def _requires(distribution_name: str) -> list[str]:
    """Wrapper around requires."""
    value = _base_requires(distribution_name)
    if value is None:
        raise PackageNotFoundError(distribution_name)
    return value


@register(ast.Import)
def check_import(node: ast.Import) -> IssueGenerator:
    """Visit an import statement."""
    for alias in node.names:
        yield from _check_module(alias.name, node)


@register(ast.ImportFrom)
def check_import_from(node: ast.ImportFrom) -> IssueGenerator:
    """Visit an import from statement."""
    if node.module and node.level == 0:
        for alias in node.names:
            module = node.module + "." + alias.name
            yield from _check_module(module, node)


def _check_module(module: str, node: ast.Import | ast.ImportFrom) -> IssueGenerator:
    options = cast(_Options, base.get_plugin().get_options())
    # if the checker was not configured, return early
    if not options.distribution_name:
        return
    # check if we should ignore the given import
    if _ignore_import(options, node):
        return

    # receive the distribution name from the import;
    # e.g. pytest for "import pytest" or gitpython for "import git"
    dist_name = _get_distribution_from_import(options, module)
    # receive the extra requirements which are configured for the current file
    # if requirements_module_extra_mapping is not use, everything is allowed
    extras = (
        _get_extras(options, node)
        if options.requirements_module_extra_mapping
        else ["*"]
    )
    import_allowed = (
        any(
            dist_name in req_list
            for req_list in options.requirements_allow_list.values()
        )
        if "*" in extras
        else any(
            dist_name in options.requirements_allow_list[extra] for extra in extras
        )
    )
    if import_allowed:
        return

    # find all extras which allow the used distribution
    extras_with_dist = [
        extra
        for extra, req_list in options.requirements_allow_list.items()
        if dist_name in req_list
    ]
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="041",
        message=(
            f"Found illegal import of {module}. "
            + (
                "The imported module is part of the projects requirements but the current "
                "module/package cannot use anything from the extra requirement(s)/group(s) "
                + ",".join(extras_with_dist)
                if extras_with_dist
                else "It is not part of the projects requirements"
            )
        ),
    )


def _get_extras(options: _Options, node: ast.Import | ast.ImportFrom) -> list[str]:
    """Return the extras which are configured for the current file."""
    extras = [INSTALL_REQUIRE_EXTRA]
    file_module = _get_module_name()
    file_identifier = _get_identifier(node)
    module_parts = _build_combinations(file_module, ".")
    identifier_parts = _build_combinations(file_identifier, "::")

    # extra mapping cascades down, so a config for foo.bar is also valid for foo.bar.baz
    # therefore we check for all part of the current file (module) if a config exists,
    # so here for "foo", "foo.bar" and "foo.bar.baz".
    # If the configuration module and the current module match exactly, we check the identifier
    # (meaning classes and functions) in the same way

    for location, activate_extras in options.requirements_module_extra_mapping.items():
        for part in module_parts:
            if location.module == file_module and location.identifier:
                for identifier_part in identifier_parts:
                    if location.identifier == identifier_part:
                        extras.extend(activate_extras)
                        break

            if location.module == part:
                extras.extend(activate_extras)
                break

    return extras


def _get_distribution_from_import(options: _Options, module: str) -> str:
    # try to find the distribution name
    # 1. look into the requirements_mapping
    #    if the module starts with any configured key followed by a dot
    #    or the module is any key
    #    e.g. module 'foo.bar.z', the key 'foo.bar' and 'foo.' would match
    # 2. extract the first part of the module (split by the first dot)
    #    e.g. for module 'pytest.mark' this would be 'pytest'
    for key, value in options.requirements_mapping.items():
        if key == module or (module.startswith(key) and module[len(key)] == "."):
            return value
    return module.split(".")[0]


def _get_identifier(node: ast.Import | ast.ImportFrom) -> str:
    # build the identifier of an import, which is the location within in an import
    # e.g. if the import is in a method foo in class A, the identifier would be A::foo
    identifiers = []
    for parent in get_parents(node):
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            identifiers.append(parent.name)
        if isinstance(parent, ast.ClassDef):
            identifiers.append(parent.name)
    return "::".join(reversed(identifiers))


@functools.lru_cache(maxsize=2)
def _build_combinations(value: str, sep: str) -> list[str]:
    # build all combinations of a string with a given separator
    # e.g. foo.bar.baz with separator '.' would return ['foo', 'foo.bar', 'foo.bar.baz']
    if not value:
        return []

    parts: list[str] = []
    current: list[str] = []
    for part in value.split(sep):
        current.append(part)
        parts.append(sep.join(current))
    return parts


def _get_module_name() -> str:
    return _get_module_name_cached(Path(base.get_plugin().filename))


@functools.lru_cache(maxsize=1)
def _get_module_name_cached(filename: Path) -> str:
    parents = [parent.stem for parent in reversed(filename.parents) if parent.stem]
    module = ".".join(parents)
    if filename.name != "__init__.py":
        module = module + "." if module else module
        module += filename.stem
    return module


def _get_from_dependency_groups() -> Iterator[tuple[str, Requirement]]:
    toml_file = base.get_plugin().get_options().pyproject_toml_file
    if not toml_file:
        return
    with open(toml_file, "rb") as fp:
        pyproject = tomllib.load(fp)
    groups_raw = pyproject.get("dependency-groups", {})
    if not groups_raw:
        return

    for group in groups_raw.keys():
        requirements = dependency_groups.resolve(groups_raw, group)
        for requirement in requirements:
            yield group, Requirement(requirement)


def _ignore_import(options: _Options, node: ast.Import | ast.ImportFrom) -> bool:
    if not options.requirements_ignore_type_checking_block:
        return False
    return any(
        isinstance(parent, ast.If)
        and isinstance(parent.test, ast.Name)
        and parent.test.id == "TYPE_CHECKING"
        for parent in get_parents(node)
    )


@register_parse_options
def parse_options(options: Namespace) -> None:
    """Parse options for this checker."""
    if not options.distribution_name:
        return

    options.requirements_mapping = _parse_mapping(options.requirements_mapping)
    options.requirements_module_extra_mapping = _parse_module_extra_mapping(
        options.requirements_module_extra_mapping
    )
    requirements_allow_list = options.requirements_allow_list = defaultdict(list)

    for req in _requires(options.distribution_name):
        requirement = Requirement(req)
        match = EXTRA_PATTERN.fullmatch(str(requirement.marker))
        extra = match.group("extra") if match else ""
        requirements_allow_list[extra].append(_normalize(requirement.name))

    for group, requirement in _get_from_dependency_groups():
        requirements_allow_list[group].append(_normalize(requirement.name))

    requirements_allow_list[INSTALL_REQUIRE_EXTRA].extend(stdlib_module_names)
    requirements_allow_list[INSTALL_REQUIRE_EXTRA].extend(options.requirements_packages)


@register_add_options
def add_options(option_manager: OptionManager) -> None:
    """Add options for this checker."""
    option_manager.add_option(
        "--distribution-name", parse_from_config=True, default=None
    )
    option_manager.add_option(
        "--requirements-mapping", parse_from_config=True, default=None
    )
    option_manager.add_option(
        "--requirements-module-extra-mapping", parse_from_config=True, default=None
    )
    option_manager.add_option(
        "--requirements-packages",
        parse_from_config=True,
        comma_separated_list=True,
        default=[],
    )
    option_manager.add_option(
        "--requirements-ignore-type-checking-block",
        parse_from_config=True,
        action="store_true",
    )


def _parse_mapping(value: str | None) -> dict[str, str]:
    mappings: dict[str, str] = {}

    if not value:
        return mappings

    for pair in value.replace("\n", "").replace("\r", "").split(","):
        if not pair:
            continue
        module, require = pair.split(":")
        mappings[module] = _normalize(require)
    return mappings


def _parse_module_extra_mapping(value: str | None) -> dict[_Location, list[str]]:
    mappings: dict[_Location, list[str]] = {}

    if not value:
        return mappings

    for pair in value.replace("\n", "").replace("\r", "").split(","):
        if not pair:
            continue
        location, extras = pair.split("|", maxsplit=1)
        module, identifier = (
            location.strip().split("::", maxsplit=1)
            if "::" in location
            else (location.strip(), None)
        )
        # mypy complains because of reasons that module is maybe None
        assert module is not None
        mappings[_Location(module, identifier)] = extras.strip().split(" ")
    return mappings


def _normalize(name: str) -> str:
    return canonicalize_name(name).replace("-", "_")
