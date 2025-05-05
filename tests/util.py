"""Utility for tests."""

from __future__ import annotations

from typing import NamedTuple

from dirty_equals import IsOneOf


class LenientIssue(NamedTuple):
    line: int | IsOneOf
    column: int | IsOneOf
    issue_number: str
    message: str
