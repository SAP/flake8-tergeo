"""Global flake8 options."""

from __future__ import annotations

import platform
from argparse import Namespace

from _flake8_tergeo.base import get_plugin
from _flake8_tergeo.flake8_types import OptionManager
from _flake8_tergeo.registry import register_add_options, register_parse_options


@register_add_options
def register_global_options(option_manager: OptionManager) -> None:
    """Add global options."""
    option_manager.add_option(
        "--python-version", parse_from_config=True, default=platform.python_version()
    )
    option_manager.add_option(
        "--auto-manage-options", parse_from_config=True, action="store_true"
    )


@register_parse_options
def parse_global_options(options: Namespace) -> None:
    """Parse the global options."""
    parts = options.python_version.split(".")
    if len(parts) != 3:
        raise ValueError("--python-version needs to specified as X.X.X")
    try:
        options.python_version = (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError as err:
        raise ValueError("--python-version must only contain numbers") from err


def get_python_version() -> tuple[int, int, int]:
    """Return the python version used for checks."""
    return get_plugin().get_options().python_version
