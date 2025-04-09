"""Script which shows the tokens of a given Python code snippet.

Usage: python scripts/show_tokens.py <code_snippet>
"""

from __future__ import annotations

import io
import sys
import tokenize

if __name__ == "__main__":
    content = sys.argv[1]
    for token in tokenize.generate_tokens(io.StringIO(content).readline):
        print(token)
