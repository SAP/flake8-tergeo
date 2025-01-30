"""Import checks."""

from __future__ import annotations

import ast
from typing import Union

from typing_extensions import TypeAlias

from _flake8_tergeo.ast_util import get_imported_modules
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register

EASTEREGG_IMPORTS = ["this", "antigravity", "__hello__", "__phello__"]
DEBUGGER_MODULES = ["pdb", "ipdb", "pudb", "debug", "pdbpp", "wdb"]
OSERROR_ALIASES = ["socket.error", "select.error"]
OBSOLETE_FUTURES = [
    "__future__.nested_scopes",
    "__future__.generators",
    "__future__.division",
    "__future__.absolute_import",
    "__future__.with_statement",
    "__future__.print_function",
    "__future__.unicode_literals",
    "__future__.generator_stop",
]
EASTEREGG_FUTURES = ["__future__.braces", "__future__.barry_as_FLUFL"]

AnyImport: TypeAlias = Union[ast.Import, ast.ImportFrom]


@register(ast.Import, ast.ImportFrom)
def check_imports(node: AnyImport) -> IssueGenerator:
    """Check imports."""
    yield from _check_c_element_tree(node)
    yield from _check_easteregg_import(node)
    yield from _check_pkg_resources(node)
    yield from _check_debugger(node)
    yield from _check_oserror_alias_import(node)
    yield from _check_unnecessary_futures(node)
    yield from _check_easteregg_futures(node)
    yield from _check_relative_imports(node)
    yield from _check_unnecessary_alias(node)


def _check_c_element_tree(node: AnyImport) -> IssueGenerator:
    if "xml.etree.cElementTree" in get_imported_modules(node):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="087",
            message="Found import of deprecated module xml.etree.cElementTree.",
        )


def _check_pkg_resources(node: AnyImport) -> IssueGenerator:
    if "pkg_resources" in get_imported_modules(node):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="015",
            message=(
                "Found import of pkg_resources "
                "which should be replaced with a proper alternative of importlib.*"
            ),
        )


def _check_easteregg_import(node: AnyImport) -> IssueGenerator:
    imports = get_imported_modules(node)
    for module in EASTEREGG_IMPORTS:
        if module in imports:
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="026",
                message=f"Found import of easteregg module {module}",
            )


def _check_debugger(node: AnyImport) -> IssueGenerator:
    imports = get_imported_modules(node)
    for module in DEBUGGER_MODULES:
        if module in imports:
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="001",
                message=f"Found debugging module {module}.",
            )


def _check_oserror_alias_import(node: AnyImport) -> IssueGenerator:
    imports = get_imported_modules(node)
    for module in OSERROR_ALIASES:
        if module in imports:
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="089",
                message=f"Found OSError alias {module}; use OSError instead.",
            )


def _check_unnecessary_futures(node: AnyImport) -> IssueGenerator:
    imports = get_imported_modules(node)
    for module in OBSOLETE_FUTURES:
        if module in imports:
            future = module.split(".", maxsplit=1)[1]
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="030",
                message=f"Found unnecessary future import {future}.",
            )


def _check_easteregg_futures(node: AnyImport) -> IssueGenerator:
    imports = get_imported_modules(node)
    for module in EASTEREGG_FUTURES:
        if module in imports:
            future = module.split(".", maxsplit=1)[1]
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="027",
                message=f"Found easteregg future import {future}.",
            )


def _check_relative_imports(node: AnyImport) -> IssueGenerator:
    if isinstance(node, ast.ImportFrom) and node.level > 0:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="057",
            message="Replace relative imports with absolute ones.",
        )


def _check_unnecessary_alias(node: AnyImport) -> IssueGenerator:
    for alias in node.names:
        if alias.name == alias.asname:
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="058",
                message="Found unnecessary import alias.",
            )
