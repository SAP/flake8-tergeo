"""Utility methods for flake8 checks and plugins."""

from __future__ import annotations

import inspect
import sys
from typing import Any

if hasattr(sys, "stdlib_module_names"):  # pragma: no cover
    stdlib_module_names = list(sys.stdlib_module_names)
else:
    import stdlib_list  # pylint: disable=import-error

    stdlib_module_names = stdlib_list.stdlib_list()


def has_add_options(clazz: type[Any]) -> bool:
    """Check if a class has an "add_options" callable."""
    return hasattr(clazz, "add_options") and callable(clazz.add_options)


def has_parse_options(clazz: type[Any]) -> bool:
    """Check if a class has an "parse_options" callable."""
    return hasattr(clazz, "parse_options") and callable(clazz.parse_options)


def is_complex_parse_options(clazz: type[Any]) -> bool:
    """Check if a class has an "parse_options" callable with at least three parameters."""
    argsspec = inspect.getfullargspec(clazz.parse_options)
    return len(argsspec.args) >= 3


def build_args(argsspec: inspect.FullArgSpec, args: dict[str, Any]) -> dict[str, Any]:
    """Build arguments for a flake8 plugin."""
    kwargs: dict[str, Any] = {}
    for arg in argsspec.args:
        if arg == "self":
            continue
        try:
            kwargs[arg] = args[arg]
        except KeyError as err:
            raise RuntimeError(f"Unsupported arg {arg}") from err
    return kwargs
