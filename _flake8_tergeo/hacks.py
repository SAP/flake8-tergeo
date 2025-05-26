from __future__ import annotations

import ast


class DummyNode(ast.AST):
    pass


def _add_python314_removed_ast_nodes():
    ast.NameConstant = DummyNode
    ast.Num = DummyNode
    ast.Str = DummyNode
