"""Reusable ast utility functions."""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from functools import cache, lru_cache
from typing import cast

from typing_extensions import TypeGuard

from _flake8_tergeo.type_definitions import AnyFunctionDef, EllipsisType


def _iter_child_nodes(node: ast.AST) -> Iterator[tuple[str, ast.AST]]:
    """Custom copy of ast.iter_child_nodes.

    In difference to the original function, this ones yields also the field name
    """
    for name, field in ast.iter_fields(node):
        if isinstance(field, ast.AST):
            yield name, field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, ast.AST):
                    yield name, item


def set_info_in_tree(tree: ast.AST) -> None:
    """Set the parents of each child node in the tree.

    The python AST doesn't provide such functionality, therefore a custom logic is needed.
    """
    for node in ast.walk(tree):
        for field_name, child in _iter_child_nodes(node):
            setattr(child, "ftp_parent", (field_name, node))  # noqa: FTB010
            setattr(  # noqa: FTB010
                child,
                "ftp_in_args_assign_annotation",
                field_name == "annotation" or in_args_assign_annotation(node),
            )
            setattr(  # noqa: FTB010
                child,
                "ftp_in_return_annotation",
                field_name == "returns" or in_return_annotation(node),
            )


def get_parent(node: ast.AST) -> ast.AST | None:
    """Return the parent of a given node or ``None``."""
    info = get_parent_info(node)
    return info[1] if info else None


def get_parent_info(node: ast.AST) -> tuple[str, ast.AST] | None:
    """Return the parent information of a given node or ``None``."""
    return getattr(node, "ftp_parent", None)


def in_annotation(node: ast.AST) -> bool:
    """Return if the node is in an annotation."""
    return in_args_assign_annotation(node) or in_return_annotation(node)


def in_args_assign_annotation(node: ast.AST) -> bool:
    """Return if the node is in an annotation."""
    return getattr(node, "ftp_in_args_assign_annotation", False)


def in_return_annotation(node: ast.AST) -> bool:
    """Return if the node is in an annotation."""
    return getattr(node, "ftp_in_return_annotation", False)


def get_parents(node: ast.AST) -> list[ast.AST]:
    """Return all parents of a node."""
    return [parent[1] for parent in get_parents_info(node)]


def get_parents_info(node: ast.AST) -> list[tuple[str, ast.AST]]:
    """Return all parents of a node."""
    parent = get_parent_info(node)
    if parent:
        return [parent] + get_parents_info(parent[1])
    return []


def get_line_range(node: ast.stmt | ast.expr) -> tuple[int, int]:
    """Return line range of a given node."""
    start_line = end_line = node.lineno
    for child in ast.walk(node):
        if hasattr(child, "lineno"):
            end_line = max(child.lineno, end_line)
            start_line = min(child.lineno, start_line)
    return start_line, end_line


def is_stub(node: AnyFunctionDef) -> bool:
    """Check if a function is a stub."""
    if isinstance(node.body[0], ast.Expr) and is_constant_node(node.body[0].value, str):
        return _is_stub_with_docstring(node)
    return _is_stub_without_docstring(node)


def _is_stub_with_docstring(node: AnyFunctionDef) -> bool:
    if len(node.body) == 1:
        return True
    if len(node.body) == 2:
        return _is_stub_statement(node.body[1])
    return False


def _is_stub_without_docstring(node: AnyFunctionDef) -> bool:
    return len(node.body) == 1 and _is_stub_statement(node.body[0])


def _is_stub_statement(node: ast.AST) -> bool:
    return (
        is_constant_node(node.value, EllipsisType)
        if isinstance(node, ast.Expr)
        else isinstance(node, (ast.Raise, ast.Pass))
    )


def stringify(node: ast.Name | ast.Attribute) -> str:
    """Stringify a given node."""
    if isinstance(node, ast.Name):
        return node.id
    if not isinstance(node.value, (ast.Name, ast.Attribute)):
        return ""
    return stringify(node.value) + "." + node.attr


def get_imports(node: ast.AST) -> list[str]:
    """Return all absolute imports of the module of the given node."""
    parents = get_parents(node)
    tree = parents[-1] if parents else node
    return _get_imports_cached(tree)


@lru_cache(maxsize=1)
def _get_imports_cached(tree: ast.AST) -> list[str]:
    imports: list[str] = []

    for child in ast.walk(tree):
        if isinstance(child, ast.Import):
            for alias in child.names:
                imports.append(alias.name)
        elif isinstance(child, ast.ImportFrom):
            if child.module is None or child.level:
                continue
            for alias in child.names:
                imports.append(child.module + "." + alias.name)

    return sorted(imports)


def is_float(node: ast.expr | None) -> TypeGuard[ast.UnaryOp]:
    """Check if a node a real float."""
    if not node:
        return False
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        node = node.operand
    return is_constant_node(node, float)


def get_imported_modules(node: ast.Import | ast.ImportFrom) -> list[str]:
    """Get all possible imported modules of an import."""
    if isinstance(node, ast.Import):
        return [name for alias in node.names for name in _split_name(alias.name)]
    if not node.module:
        return []
    return _split_name(node.module) + [
        node.module + "." + alias.name for alias in node.names
    ]


def _split_name(name: str) -> list[str]:
    names = []
    current_name = ""
    for index, part in enumerate(name.split(".")):
        if index == 0:
            current_name = part
        else:
            current_name += "." + part
        names.append(current_name)
    return names


@cache
def _get_import_map(module: str, attr: str) -> Mapping[str, Iterable[str]]:
    return _get_import_map_uncached(module, attr)


def _get_import_map_uncached(
    module: str, attr: str, result: defaultdict[str, set[str]] | None = None
) -> Mapping[str, Iterable[str]]:
    result = result or defaultdict(set)
    current_module_parts = []
    module_parts = module.split(".")
    full_name = module + "." + attr

    while module_parts:
        current_part = module_parts.pop(0)
        current_module_parts.append(current_part)
        current_module = ".".join(current_module_parts)

        result[full_name].add(current_module)

        current_attr = current_part + "." + ".".join(module_parts)
        if not current_attr.endswith("."):
            current_attr += "."
        current_attr += attr
        result[current_attr].add(current_module)

    first_attr_part = attr.split(".", maxsplit=1)[0]
    result[attr].add(module + "." + first_attr_part)

    if module == "typing":
        _get_import_map_uncached("typing_extensions", attr, result)
    return result


def is_expected_node(
    node: ast.AST, module: str, attr: str
) -> TypeGuard[ast.Attribute | ast.Name]:
    """Check if a node is the one which is needed and is imported."""
    if not isinstance(node, (ast.Attribute, ast.Name)):
        return False
    name = stringify(node)
    data = _get_import_map(module, attr)
    if name not in data:
        return False

    return any(
        name == possible_name
        and any(imp in get_imports(node) for imp in possible_imports)
        for possible_name, possible_imports in data.items()
    )


def is_constant_node(
    node: ast.AST | None, types_: type | tuple[type, ...]
) -> TypeGuard[ast.Constant]:
    """Check if a node is a constant node."""
    if not node:
        return False
    return isinstance(node, ast.Constant) and isinstance(node.value, types_)


def has_future_annotations(node: ast.AST) -> bool:
    """Check if a file has a __future__ import of annotations."""
    module = cast(ast.Module, get_parents(node)[-1])
    return any(
        isinstance(child, ast.ImportFrom)
        and child.module == "__future__"
        and any(name.name == "annotations" for name in child.names)
        for child in module.body
    )


def in_type_checking_block(node: ast.AST) -> bool:
    """Check if a node is in a TYPE_CHECKING block."""
    return any(
        isinstance(parent, ast.If)
        and is_expected_node(parent.test, "typing", "TYPE_CHECKING")
        for parent in get_parents(node)
    )


def is_in_type_statement(node: ast.AST) -> bool:
    """Check if a node is in a type alias."""
    if sys.version_info < (3, 12):
        return False  # type statement is not available in 3.11
    return any(isinstance(parent, ast.TypeAlias) for parent in get_parents(node))


def is_in_type_alias(node: ast.AST) -> bool:
    """Check if a node is in a type alias."""
    result = [
        parent for parent in get_parents(node) if isinstance(parent, ast.AnnAssign)
    ]
    if not result:
        return False
    return is_expected_node(result[0].annotation, "typing", "TypeAlias")


def flatten_bin_op(node: ast.BinOp) -> list[ast.AST]:
    """Flatten a binary operation node into a list of its operands."""
    nodes = []
    if isinstance(node.left, ast.BinOp):
        nodes.extend(flatten_bin_op(node.left))
    else:
        nodes.append(node.left)
    nodes.append(node.right)
    return nodes
