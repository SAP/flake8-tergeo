"""Script which shows the AST of a given Python code snippet.

Usage: python scripts/show_ast.py <code_snippet>
"""

from __future__ import annotations

import ast
import sys

import astpretty

if __name__ == "__main__":
    content = sys.argv[1]
    tree = ast.parse(content)
    astpretty.pprint(tree, show_offsets=True)
