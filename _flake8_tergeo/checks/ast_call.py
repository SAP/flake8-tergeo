"""Call checks."""

from __future__ import annotations

import ast
from typing import cast

from _flake8_tergeo.ast_util import (
    get_imports,
    get_parent,
    get_parents,
    is_constant_node,
    is_expected_node,
    stringify,
)
from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.global_options import get_python_version
from _flake8_tergeo.registry import register

BAD_CALLS = (
    "__import__",
    "compile",
    "copyright",
    "credits",
    "exit",
    "help",
    "quit",
    "reveal_type",
)
_POINTLESS_STAR_NODES = (ast.Dict, ast.List, ast.Set, ast.Tuple, ast.Constant)
BAD_SUBPROCESS_ALIASES = (
    "popen",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
)
RE_FUNCTIONS = (
    "search",
    "match",
    "fullmatch",
    "split",
    "findall",
    "finditer",
    "sub",
    "subn",
)
RE_PARENTS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.For, ast.While, ast.Lambda)


@register(ast.Call)
def check_call(node: ast.Call) -> IssueGenerator:
    """Visit a call statement."""
    yield from _check_os_walk(node)
    yield from _check_urlparse(node)
    yield from _check_multiprocessing_set_start_method(node)
    yield from _check_lru_cache(node)
    yield from _check_contextlib_wraps(node)
    yield from _check_bad_call(node)
    yield from _check_float_nan(node)
    yield from _check_print(node)
    yield from _check_print_empty_string(node)
    yield from _check_pp(node)
    yield from _check_pprint(node)
    yield from _check_pretty_printer(node)
    yield from _check_range(node)
    yield from _check_super_call(node)
    yield from _check_open_statement(node)
    yield from _check_debug_builtin(node)
    yield from _check_isinstance(node)
    yield from _check_string_format(node)
    yield from _check_primitive_call(node)
    yield from _check_namedtuple(node)
    yield from _check_capture_output(node)
    yield from _check_universal_newlines(node)
    yield from _check_namedtuple_legacy_call(node)
    yield from _check_typeddict_legacy_call(node)
    yield from _check_pallets_abort(node)
    yield from _check_pointless_single_starred(node)
    yield from _check_pointless_double_starred(node)
    yield from _check_simpler_path(node)
    yield from _check_primitive_function_call(node)
    yield from _check_deprecated_decorator(node)
    yield from _check_bad_subprocess_aliases(node)
    yield from _check_typevar_usage(node)
    yield from _os_error_with_errno(node)
    yield from _check_string_template(node)
    yield from _check_regex_compile_in_function(node)
    yield from _check_regex_module_function_with_constant(node)


def _check_os_walk(node: ast.Call) -> IssueGenerator:
    """Check a os.walk call."""
    if not is_expected_node(node.func, "os", "walk"):
        return

    on_error = [keyword for keyword in node.keywords if keyword.arg == "onerror"]
    if not on_error:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="081",
            message="Missing onerror keyword in os.walk call.",
        )


def _check_urlparse(node: ast.Call) -> IssueGenerator:
    """Check a urlparse call."""
    if not is_expected_node(node.func, "urllib.parse", "urlparse"):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="014",
        message="Call of urlparse should be replaced with urlsplit.",
    )


def _check_multiprocessing_set_start_method(node: ast.Call) -> IssueGenerator:
    """Check multiprocessing.set_start_method call."""
    if not is_expected_node(node.func, "multiprocessing", "set_start_method"):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="098",
        message="Found usage of multiprocessing.set_start_method. "
        "Use a multiprocessing Context instead.",
    )


def _check_lru_cache(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "functools", "lru_cache"):
        return
    if len(node.args) == 1 and node.keywords:
        # maxsize is given as arg and typed as kwarg
        return
    if len(node.args) > 1:
        # typed is given as arg
        return
    if len(node.keywords) > 1:
        # typed is given as kwarg
        return

    for keyword in node.keywords:
        if keyword.arg == "maxsize":
            yield from _check_lru_expression(keyword.value, node)

    if node.args:
        yield from _check_lru_expression(node.args[0], node)


def _check_lru_expression(value: ast.expr, node: ast.Call) -> IssueGenerator:
    if is_constant_node(value, type(None)):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="073",
            message=("Use functools.cache instead."),
        )


def _check_contextlib_wraps(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "contextlib", "wraps"):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="063",
        message=(
            "Found usage/import of contextlib.wraps. "
            "This is a not a re-exported import. Use the original functools.wraps instead."
        ),
    )


def _check_bad_call(node: ast.Call) -> IssueGenerator:
    if isinstance(node.func, ast.Name) and node.func.id in BAD_CALLS:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="045",
            message=f"Found bad call to {node.func.id}.",
        )


def _check_float_nan(node: ast.Call) -> IssueGenerator:
    if (
        isinstance(node.func, ast.Name)
        and node.func.id == "float"
        and len(node.args) == 1
        and is_constant_node(node.args[0], str)
        and node.args[0].value.upper() == "NAN"
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="038",
            message="Instead of float('NaN') use math.nan.",
        )


def _check_print(node: ast.Call) -> IssueGenerator:
    if isinstance(node.func, ast.Name) and node.func.id == "print":
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="050",
            message="Found print statement.",
        )


def _check_pp(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "pprint", "pp"):
        return
    yield from _check_pretty_calls(node, "pprint.pp", "052")


def _check_pprint(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "pprint", "pprint"):
        return
    yield from _check_pretty_calls(node, "pprint.pprint", "051")


def _check_pretty_printer(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "pprint", "PrettyPrinter"):
        return
    yield from _check_pretty_calls(node, "pprint.PrettyPrinter", "053")


def _check_pretty_calls(node: ast.Call, name: str, issue_number: str) -> IssueGenerator:
    if any(keyword.arg == "stream" for keyword in node.keywords):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number=issue_number,
        message=f"Found {name} statement which prints on stdout.",
    )


def _check_range(node: ast.Call) -> IssueGenerator:
    if not isinstance(node.func, ast.Name):
        return
    if len(node.args) != 2:
        return

    arg = node.args[0]
    if isinstance(arg, ast.UnaryOp) and isinstance(arg.op, (ast.USub, ast.UAdd)):
        arg = arg.operand
    name = node.func.id

    if name == "range" and isinstance(arg, ast.Constant) and arg.value == 0:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="092",
            message="Remove 0 as starting point in range(), as it starts at 0 by default.",
        )


def _check_super_call(node: ast.Call) -> IssueGenerator:
    if (
        isinstance(node.func, ast.Name)
        and node.func.id == "super"
        and len(node.args) > 1
        and cast(ast.Name, node.args[1]).id == "self"
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="070",
            message="Use `super()` instead of `super(__class__, self)`.",
        )


def _check_open_statement(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "io", "open"):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="088",
        message="Found unnecessary use of io.open; use open instead.",
    )


def _check_debug_builtin(node: ast.Call) -> IssueGenerator:
    if isinstance(node.func, ast.Name) and node.func.id == "breakpoint":
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="002",
            message=f"Found debugging builtin {node.func.id}.",
        )


def _check_isinstance(node: ast.Call) -> IssueGenerator:
    if not isinstance(node.func, ast.Name):
        return
    if node.func.id != "isinstance":
        return
    if len(node.args) != 2:
        return
    if not isinstance(node.args[1], ast.Tuple):
        return
    if len(node.args[1].elts) != 1:
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="025",
        message=(
            "Calling isinstance with a one-element tuple can be simplified. "
            "Instead of a tuple, just use the element directly."
        ),
    )


def _check_string_format(node: ast.Call) -> IssueGenerator:
    """Check a call statement."""
    if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        if is_constant_node(node.func.value, str):
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="061",
                message="String literal formatting using format method.",
            )

        elif (
            isinstance(node.func.value, ast.Name)
            and node.func.value.id == "str"
            and is_constant_node(node.args[0], str)
        ):
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="062",
                message="String formatting with str.format.",
            )


def _check_primitive_call(node: ast.Call) -> IssueGenerator:
    if not isinstance(node.func, ast.Name):
        return
    if len(node.args) != 1:
        return

    arg = node.args[0]
    if isinstance(arg, ast.UnaryOp) and isinstance(arg.op, (ast.USub, ast.UAdd)):
        arg = arg.operand
    name = node.func.id

    if (is_constant_node(arg, str) or isinstance(arg, ast.JoinedStr)) and name == "str":
        yield _get_primitive_call_issue(node, "083", name)
    elif (
        # bool is a subclass of int, so we need to check that it's not a bool
        is_constant_node(arg, int)
        and not isinstance(arg.value, bool)
        and name == "int"
    ):
        yield _get_primitive_call_issue(node, "084", name)
    elif is_constant_node(arg, float) and name == "float":
        yield _get_primitive_call_issue(node, "085", name)
    elif is_constant_node(arg, bool) and name == "bool":
        yield _get_primitive_call_issue(node, "086", name)
    elif is_constant_node(arg, bytes) and name == "bytes":
        yield _get_primitive_call_issue(node, "109", name)


def _get_primitive_call_issue(node: ast.Call, issue_number: str, name: str) -> Issue:
    return Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number=issue_number,
        message=f"Found unnecessary use of {name}() on a constant",
    )


def _check_primitive_function_call(node: ast.Call) -> IssueGenerator:
    if not isinstance(node.func, ast.Name):
        return
    if len(node.args) != 0:
        return

    name = node.func.id
    if name == "str":
        yield _get_primitive_function_call_issue(node, "110", name, '""')
    elif name == "int":
        yield _get_primitive_function_call_issue(node, "111", name, "0")
    elif name == "float":
        yield _get_primitive_function_call_issue(node, "112", name, "0.0")
    elif name == "bool":
        yield _get_primitive_function_call_issue(node, "113", name, "False")
    elif name == "bytes":
        yield _get_primitive_function_call_issue(node, "114", name, 'b""')


def _get_primitive_function_call_issue(
    node: ast.Call, issue_number: str, name: str, constant: str
) -> Issue:
    return Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number=issue_number,
        message=f"Replace {name}() with the constant <{constant}> directly.",
    )


def _check_namedtuple(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "collections", "namedtuple"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="065",
        message="Use typing.NamedTuple instead of collections.namedtuple.",
    )


def _check_capture_output(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "subprocess", "run"):
        return

    # check if both stdout and stderr are present and both have the pipe variable assigned
    if [
        isinstance(keyword.value, (ast.Name, ast.Attribute))
        and is_expected_node(keyword.value, "subprocess", "PIPE")
        for keyword in node.keywords
        if keyword.arg in {"stdout", "stderr"}
    ] != [True, True]:
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="068",
        message="Replace 'stdout=PIPE and stderr=PIPE' with 'capture_output=True'.",
    )


def _check_universal_newlines(node: ast.Call) -> IssueGenerator:
    if not (
        is_expected_node(node.func, "subprocess", "Popen")
        or is_expected_node(node.func, "subprocess", "run")
    ):
        return
    if not any(keyword.arg == "universal_newlines" for keyword in node.keywords):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="075",
        message="Replace 'universal_newlines' with 'text'.",
    )


def _check_namedtuple_legacy_call(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "typing", "NamedTuple"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="017",
        message="Extend typing.Namedtuple instead of calling it.",
    )


def _check_typeddict_legacy_call(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "typing", "TypedDict"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="018",
        message="Extend typing.TypedDict instead of calling it.",
    )


def _check_pallets_abort(node: ast.Call) -> IssueGenerator:
    if not (
        is_expected_node(node.func, "flask", "abort")
        or is_expected_node(node.func, "werkzeug.exceptions", "abort")
    ):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="200",
        message="Instead of using abort raise the appropriate exception directly.",
    )


def _check_pointless_single_starred(node: ast.Call) -> IssueGenerator:
    for arg in node.args:
        if not isinstance(arg, ast.Starred):
            continue
        if not isinstance(arg.value, _POINTLESS_STAR_NODES):
            continue
        if isinstance(arg.value, ast.Constant) and not isinstance(
            arg.value.value, (str, bytes)
        ):
            continue
        yield Issue(
            line=arg.lineno,
            column=arg.col_offset,
            issue_number="059",
            message=(
                "Using starred expression on a constant structure is pointless. "
                "Rewrite the code to be flat."
            ),
        )


def _check_pointless_double_starred(node: ast.Call) -> IssueGenerator:
    for keyword in node.keywords:
        if keyword.arg is not None:
            continue
        if not isinstance(keyword.value, ast.Dict):
            continue
        # check that all keys in the dict are strings -> constant dict
        if not all(is_constant_node(key, str) for key in keyword.value.keys):
            continue

        yield Issue(
            line=keyword.lineno,
            column=keyword.col_offset,
            issue_number="059",
            message=(
                "Using starred expression on a constant structure is pointless. "
                "Rewrite the code to be flat."
            ),
        )


def _check_print_empty_string(node: ast.Call) -> IssueGenerator:
    if (
        isinstance(node.func, ast.Name)
        and node.func.id == "print"
        and len(node.args) == 1
        and is_constant_node(node.args[0], str)
        and node.args[0].value == ""
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="100",
            message="Calling print with an empty string can be simplified to 'print()'.",
        )


def _check_simpler_path(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "pathlib", "Path"):
        return
    if node.keywords:
        # if any keyword is given, it's not a simple Path call
        return
    if not node.args or len(node.args) > 1:
        return
    if not is_constant_node(node.args[0], str) or node.args[0].value != ".":
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="102",
        message="Calling the path constructor with '.' can be simplified to 'Path()'.",
    )


def _check_deprecated_decorator(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "warnings", "warn"):
        return
    if len(node.args) < 2:
        return

    category = node.args[1]
    if not isinstance(category, ast.Name):
        return
    if stringify(category) != "DeprecationWarning":
        return

    parent = get_parent(node)
    if not parent:  # pragma: no cover
        return
    parent = get_parent(parent)
    if not isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return

    if any(
        is_expected_node(decorator, "warnings", "deprecated")
        or is_expected_node(decorator, "typing_extensions", "deprecated")
        for decorator in parent.decorator_list
    ):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="117",
            message="The outer function is already decorated with 'deprecated'. "
            "Remove the warnings.warn call to avoid duplicate warnings.",
        )
    else:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="118",
            message="Consider using the 'deprecated' decorator instead of warnings.warn.",
        )


def _check_bad_subprocess_aliases(node: ast.Call) -> IssueGenerator:
    if not any(
        is_expected_node(node.func, "os", func) for func in BAD_SUBPROCESS_ALIASES
    ):
        return

    assert isinstance(node.func, (ast.Name, ast.Attribute))
    name = stringify(node.func)
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="121",
        message=f"Function {name} should be replaced with function of the subprocess module.",
    )


def _check_typevar_usage(node: ast.Call) -> IssueGenerator:
    if get_python_version() < (3, 12):
        return
    if not is_expected_node(node.func, "typing", "TypeVar"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="127",
        message="Use the new generic syntax instead of TypeVar.",
    )


def _os_error_with_errno(node: ast.Call) -> IssueGenerator:
    if not isinstance(node.func, ast.Name):
        return
    if stringify(node.func) != "OSError":
        return
    if len(node.args) == 0:
        return
    if not isinstance(node.args[0], ast.Attribute):
        return
    if not stringify(node.args[0]).startswith("errno."):
        return
    if "errno" not in get_imports(node):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="019",
        message=(
            "The constructor of OSError has no special handling for errno values, it just "
            "treats them as error message. To set the errno attribute, set it on the OSError "
            "instance after the call."
        ),
    )


def _check_string_template(node: ast.Call) -> IssueGenerator:
    if get_python_version() < (3, 14):
        return
    if not is_expected_node(node.func, "string", "Template"):
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="130",
        message="Use t-strings instead of string.Template.",
    )


def _check_regex_compile_in_function(node: ast.Call) -> IssueGenerator:
    if not is_expected_node(node.func, "re", "compile"):
        return
    if len(node.args) == 0:
        return
    if not is_constant_node(node.args[0], str):
        return
    if not any(isinstance(parent, RE_PARENTS) for parent in get_parents(node)):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="131",
        message="Instead of compiling the regex each time the function is called, "
        "compile it once on module level and use the compiled version.",
    )


def _check_regex_module_function_with_constant(node: ast.Call) -> IssueGenerator:
    if not any(
        is_expected_node(node.func, "re", func_name) for func_name in RE_FUNCTIONS
    ):
        return
    if len(node.args) == 0:
        return
    if not is_constant_node(node.args[0], str):
        return
    if not any(isinstance(parent, RE_PARENTS) for parent in get_parents(node)):
        return

    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="132",
        message=(
            "Instead of calling the regex function with a constant string, which is compiled each "
            "time the outer function is called, store the compiled version of the regex in a "
            "constant variable and use that instead."
        ),
    )
