
# Checks

## Codes

* FTP000: internal errors
* FTP001 - FTP199: general purpose checks
* FTP200 - FTP219: `flask` and `werkzeug` checks
* FTP220 - FTP239: `requests` checks
* FTP300 - FTP399: docstring checks

## FTP000
Error while loading this plugin or any other internal error.

## FTP001
Checks if one of the debug modules `pdb`, `ipdb`, `pudb`, `wdb`, `pdbpp` and `debugger` is used.
Debug modules should not be left in the code.

## FTP002
Checks if the debug builtin `breakpoint` is used.
A breakpoint should not be left in code as its halts the program leading to a stop.

## FTP003
Checks for usage of `datetime.datetime.utcnow` without a `tz` parameter.
The value returned by it is in current UTC time but without any timezone assigned.
Instead call `datetime.datetime.now` with a timezone parameter (`tz`).

## FTP004
Checks that the module/file name follows the PEP-8 convention.

## FTP005
Finds duplicate class fields (multiple assigns to the same name in the class body).
Most likely this is a bug or duplicated code line.
Note, that nNo functions or blocks are checked.

## FTP006
Finds any usage of unicode directionality formatting characters.
These characters are used to display left-to-right/right-to-left text in the same line and are
interpreted by the bidi algorithm.
However, having these characters in source code can lead to attacks like early
returns because the code is executed in another way than written.
A normal code review will not detect these issues.
The easiest way is to ban these characters.
For details see [this paper](https://trojansource.codes/trojan-source.pdf>).

## FTP007
Checks for usage of `datetime.datetime.utcfromtimestamp` without the `tz` parameter.
The returned value is the current UTC time but without any timezone assigned.
Instead call `datetime.datetime.fromtimestamp` with the timezone parameter (`tz`).

## FTP008
Checks for unnecessary parenthesis, like `print((1,2,3))` or `return (a, b)`.
By default, the parenthesis of a return of a single element tuple is not reported as with parenthesis
the code is more clear.
This can be disabled by using `disallow-parens-in-return-single-element-tuple`

## FTP009
Checks for classes extending `BaseException`. Extend `Exception` instead.

## FTP010
Checks if a disallowed developer comment identifier is used.
Please refer to the developer comment configuration.

## FTP011
Checks if the tracking id reference in a developer comment is missing.
Please refer to the developer comment configuration.

## FTP012
Checks if an invalid tracking id reference in a developer comment is used.
Please refer to the developer comment configuration.

## FTP013
Checks if the description of a developer comment is missing.
Please refer to the developer comment configuration.

## FTP014
Checks for calls of `urllib.parse.urlparse`.
This function can parse a special `;parameters` part inside the url path which is not recommended.
The function `urllib.parse.urlsplit` does basically the same but ignores the
`parameters` part and is therefore faster.

## FTP015
Checks for imports of `pkg_resources`.
This module should not be used anymore as better and faster alternatives are available in
`importlib` and its backports.

## FTP016
Finds usage of python2 metaclass declaration with `__metaclass__` inside the class body.
Use `metaclass=` in the class signature instead.

## FTP017
Finds legacy calls of `typing.NamedTuple`.
Instead, extend `typing.NamedTuple` by creating a new class.

## FTP018
Finds legacy calls of `typing.TypedDict`.
Instead, extend `typing.TypedDict` by creating a new class.

## FTP019
Checks if `OSError` is called with an `errno` constant as the first argument, e.g. `OSError(errno.ENOENT)`.
The parameter is not set as `errno` attribute on the exception but used value for the error message instead.
To properly set the `errno` attribute it must be set on the exception instance after initialization: `error=OSError(); error.errno=errno.ENOENT`.

## FTP020
Checks if an encoding comment (`# -*- coding: utf-8 -*-`) is used.
These comments are not needed in python 3 anymore.

## FTP021
Checks if a string value (or a part of it) can be replaced with `string.ascii_letters`.

## FTP022
Checks if a string value (or a part of it) can be replaced with `string.ascii_lowercase`.

## FTP023
Checks if a string value (or a part of it) can be replaced with `string.ascii_uppercase`.

## FTP024
Checks if a string value (or a part of it) can be replaced with `string.digits`.

## FTP025
Checks for `isinstance` calls with an one-element tuple.
Replace with tuple with the exact value instead and save the time which is needed to construct
and iterate over the tuple.

## FTP026
Checks for imports of the following easteregg modules
- `this`
- `antigravity`
- `__hello__`
- `__phello__`

## FTP027
Checks for if any of the following easteregg are imported over the `__future__` module
- `braces`
- `barry_as_FLUFL`.

## FTP028
Finds empty doc comments (`#:`).

## FTP029
Finds `enumeration` loops where the index variable is named `_`.
Use a classical `for` loop instead.

## FTP030
Checks if any unnecessary future import is used.

## FTP031
Checks if percentage formatting is used in logging calls.

## FTP032
Checks if a f-string is used in logging calls.

## FTP033
Checks if str.format is used in logging calls.

## FTP034
Checks if `exc_info=True` is used in `.exception()` logging calls.
This argument is redundant.

## FTP035
Checks if the deprecated logging method `.warn()` is used.

## FTP036
Checks if `exc_info=True` is used in error logging calls.
Use `.exception()` instead.

## FTP037
Checks if keys used in the `extra` dict of logging calls clashes with existing
`logging.LogRecord` fields.
This can lead to errors during runtime.

## FTP038
Checks if `float('NaN')` is used.
Use `math.nan` instead.

## FTP039
Checks if a dunder is used in the middle of the name like `a__b`.
Double underscores at the start and at the end are ignored.

## FTP040
Checks if a file is in a folder without an \_\_init\_\_.py file.
The error is reported on the first line of the file.
If files are checked which should not be part of a namespace package (e.g. setup.py), a *noqa*
comment or "per-file-ignores" can be used.

## FTP041
Checks if a module is used which is not specified as a requirement.
Please refer to the requirement check configuration.

## FTP042
Checks if a class defines a magic method like `__hex__` which is legacy from python2 and is no
longer needed.

## FTP043
Checks if a function starting with `get_` has no return or yield statement.
Consider to rename the function as the name implies a return value.
A function will be ignored, if it's a stub (e.g. just has a pass statement or only throws an exception)

## FTP044
Checks if an exception is raised from itself, e.g. `raise exc from exc`.

## FTP045
Checks if a interactive python function is called
- `help`
- `exit`

## FTP046
Checks if an except block only contains a reraise of the caught exception.
Remove the try-except as it does not anything.

## FTP047
Checks if a too generic exception (`Exception` and `BaseException`) is raised.
Consider to raise a more concrete exception instead.

## FTP048
Checks if a float is used as a dict key.
Floats have precision errors, so using them as keys is unreliable and can lead to errors.

## FTP049
Checks if a single element unpacking is used (e.g. `(a,) = my_list`).
It can be simplified to `a = mylist[0]`

## FTP050
Checks if a `print` statement is used.

## FTP051
Checks if a `pprint.pprint` statement is used.

## FTP052
Checks if a `pprint.pp` statement is used.

## FTP053
Checks if a `pprint.PrettyPrinter` statement is used.

## FTP054
Checks if a union type annotation can utilize the new syntax of PEP 604.
For example, `a: Union[Foo, Bar]` can be rewritten to `a: Foo|bar`.
This check is only active when at least one of the following conditions is true:
* running python 3.10+
* a `from __future__ import annotations` import is present in the module
* the current code is inside a `typing.TYPE_CHECKING` block

Also, the check will only consider type annotations (to prevent invalid syntax) if
at least one of the following conditions is true:
* python 3.9 or below is used
* the code is not inside a `typing.TYPE_CHECKING` block

## FTP055
Checks if an optional type annotations can utilize the new syntax of PEP 604.
For example, `a: Optional[Foo]` can be rewritten to `a: Foo|None`.
For more details see `FTP054`.

## FTP056
Checks if a builtin alias in the `typing` module can be rewritten as the builtin itself
as of PEP 585.
E.g. `typing.List[str]` can be changed to `list[str]`.

This check is only active when at least one of the following conditions is true:
* running python 3.9+
* a `from __future__ import annotations` import is present in the module
* the current code is inside a `typing.TYPE_CHECKING` block

Also, the check will only consider type annotations (to prevent invalid syntax) if
at least one of the following conditions is true:
* the code is not inside a `typing.TYPE_CHECKING` block

## FTP057
Checks if relative imports are used.

## FTP058
Checks if an unnecessary import alias is used, e.g. `import foo as foo`.

## FTP059
Checks if an argument in a function call has a pointless starred expression.
For single starred expressions, lists, dicts, tuples, sets, strings and bytes are checked.
As an example, `foo(*[1, 2, 3])` can be simplified to `foo(1, 2, 3)`.
For double starred expressions, only dicts are checked.
An issue is only raised if all keys of the dict are strings, else the dict is not considered
static and will be ignore.
As an example, `foo(**{'a': 1, 'b': 2})` can be simplified to `foo(a=1, b=2)`.

## FTP060
Checks if a percentage formatting is used

## FTP061
Checks if `"".format()` is used

## FTP062
Checks if `str.format` is used

## FTP063
Check if `contextlib.wraps` is used. The call will work at runtime, but `wraps` comes
originally from `functools.wraps` and `contextlib` doesn't re-export it, so it
should be considered as an implementation detail which is not stable.
Therefore `functools.wraps` should be used.

## FTP064
Check if `__debug__` is used. This constant is false when python is not started in optimized
`-O` mode. Because this mode is basically never used and having code which only runs when not
running in a special mode can have unexpected side effects, this constant should not be used.

## FTP065
Check if `collections.namedtuple` is used. `typing.NamedTuple` should be used
instead, since it integrates nicer with IDE's and type checkers

## FTP066
Check if an `enum.Enum` subclass is used which also extends `int`, so e.g.
`class MyEnum(Enum, int)`.
For that the alias `enum.IntEnum` can be used

## FTP067
Check if an `enum.Enum` subclass is used which also extends `str`, so e.g.
`class MyEnum(Enum, str)`.
For that the alias `enum.StrEnum` can be used.
The check is only active for python3.11+

## FTP068
Check if a call of `subprocess.run` has the value `subprocess.PIPE` assigned
to both `stdout` and `stderr`. In this case, it can be simplified to `capture_output=True`.

## FTP069
Check if a variable has a name which can lead to confusion like `pi = 5` or `nan = 4`.

## FTP070
Checks for super calls with arguments

## FTP071
Check for assign and return statements.
Normally the check also finds statements like `a: int = 2; return a`.
To configure the step to ignore assignments with annotations, use `ignore-annotation-in-assign-return`.
By default the check is disabled if the variable name happens to be part of a global/nonlocal statement.
The check is also suppressed, if the assign-return is part of a `try` block and in the
corresponding `finally` block the variable is used

## FTP072
Checks for unicode string prefixes like `u"abc"`

## FTP073
Checks for the usage of `functools.lru_cache` which can be replaced with
`functools.cache`.
The check is only active if `functools.lru_cache` is somehow imported.

## FTP074
Checks if a `functools.cache` or `functools.lru_cache` is used on a class method.
Since the `self` argument is cached as well, garbage collection is blocked, leading to memory leaks.
If the method is decorated with `staticmethod` or `classmethod`, the issue doesn't happen.
Note, that the check only considers methods which are defined as a direct child of a class.

## FTP075
Check if `subprocess.run` or `subprocess.Popen` is called with `universal_newlines`.
This keyword argument can be replaced with `text` which is more readable

## FTP076
Checks for import of `from re import DEBUG` or usage of `re.DEBUG`

## FTP078
Checks for type comments which should be replaced by annotations. `type:ignore` is ignored

## FTP077
Check if in a type annotation or type alias which contains a union, `None` always comes last.
For instance `a: int|float|None` is okay, but `a: int|None|float` is not.
This check does not consider `typing.Optional`

## FTP079
Checks for unnecessary lambda statement which can be replaced with their built-in function
alternative, e.g. `lambda: []` with `list`

## FTP080
Checks for implicit concatenated strings on the same line

## FTP081
Checks for missing `onerror` keyword in `os.walk`.
The check is only active if `os.walk` is somehow imported.

## FTP082
Checks for unnecessary usage of `metaclass=abc.ABCMeta`, which can be simplified to `abc.ABC`

## FTP083
Checks for unnecessary usage of `str()`, like `str("a")`

## FTP084
Checks for unnecessary usage of `int()`, like `int(1)`

## FTP085
Checks for unnecessary usage of `float()`, like `float(1.1)`

## FTP086
Checks for unnecessary usage of `bool()`, like `bool(True)`

## FTP087
Checks for imports of `xml.etree.cElementTree`

## FTP088
Checks for the usage of `io.open` which can be simplified to `open`.

## FTP089
Checks for the usage of `OSError` aliases
`EnvironmentError`, `IOError` and `WindowsError`.
In addition, it also finds usage and imports of `socket.error` and `select.error`.
In this case, calls like `raise socket.error()` are not checked.

## FTP090
Checks for unsorted `__all__` attributes on any level.
The check is only done if the type is a list, tuple or set during parsing
(e.g. `list` is a function and not a list during parsing).
Only items which are strings are used in the sort check, all others are ignored.

## FTP091
Checks if backslashes are used to split long lines.

## FTP092
Checks for unnecessary usage of 0 as starting point with no step size defined
in `range` call.

## FTP093
Find functions starting with `is_/have_/has_/can_` which have a non-boolean return type.
`typing.TypeGuard` is accepted as an alternative to a boolean.
Functions with no return type annotation are ignored.

## FTP094
Find cases where the `__slot__` attribute is assigned something else than a tuple or dict,
like `__slots__ = []` or `__slots__ = get_slots()`.
In general, using e.g. a list or single string is fine, but always using a tuple or dict
is more consistent and recommended

## FTP095
Checks for unnecessary use of unpack operators.

## FTP096
Find functions which are decorated with `property`, `classmethod` or
`staticmethod` but are outside of a class.

## FTP097
Find enums without `enum.unique` decorator to make sure no duplicate values are assigned.

## FTP098
Checks for usage of `multiprocessing.set_start_method`.
A multiprocessing Context should be used instead.

## FTP099
Since python 3.11 the `datetime.timezone.utc` constant is also accessible with
`datetime.UTC` which is found by this check

## FTP100
Find `print("")` which can be simplified to `print()`

## FTP101
Find unpack operators inside of a dict which can be rewritten with the dict union operator.
E.g. `{**a, **b}` can be rewritten to `a|b` and `{**a, 'b': 2}` to `a|{'b': 2}`.
The check ignores unpacks in the middle of the dict, e.g. `{'a': 1, **b, 'c': 3}`.
This check is only active when running python 3.9+.

## FTP102
Find `Path(".")` of `pathlib.Path` which can be simplified to `Path()`

## FTP103
Find usage of the OS dependent `pathlib` classes `pathlib.PosixPath`,
`pathlib.WindowsPath`, `pathlib.PurePosixPath` and
`pathlib.PureWindowsPath`.
These classes can be replaced with `pathlib.Path` and `pathlib.PurePath`,
because they are OS independent and create the correct OS dependent class behind the scenes

## FTP104
Finds `typing.Never` and `typing.NoReturn` in unions in type annotations and type alias.
These types are redundant in unions and can be removed.

## FTP105
Find nested `typing.Union` types like `Union[Union[int, str], float]`.
These can be simplified to `Union[int, str, float]`

## FTP106
Find `typing.Union` with a single element, e.g. `Union[int]`. This can be simplified to
`int`

## FTP107
Find usage of `typing.Never` in return annotations.
Instead use `typing.NoReturn`

## FTP108
Find usage of `typing.NoReturn` in non-return annotations (arguments and assignments).
Instead use `typing.Never`

## FTP109
Checks for unnecessary usage of `bytes()`, like `bytes(b'abc'')`

## FTP110
Find `str()` which can be simplified to `""`

## FTP111
Find `int()` which can be simplified to `0`

## FTP112
Find `float()` which can be simplified to `0.0`

## FTP113
Find `bool()` which can be simplified to `False`

## FTP114
Find `bytes()` which can be simplified to `b""`

## FTP115
Find invisible unicode characters in source code

## FTP116
Find named expressions (walrus operator `:=`) in assert statements

## FTP117
Find functions calling `warnings.warn` but which are also decorated with
`warnings.deprecated` or `typing_extensions.deprecated`

## FTP118
Find functions calling `warnings.warn` but which could use
`warnings.deprecated` or `typing_extensions.deprecated`

## FTP119
Checks for unsorted `__slots__` attributes on any level.
The check is only done if the type is a list, tuple or set during parsing.
Only items which are strings are used in the sort check; all others are ignored.

## FTP120
Find assignments to `__slots__` outside of a class. The assignment can be wrapped into
constructs like an `if` but the first *container* needs to be a class and not a function or
module

## FTP121
Find calls of soft-deprecated `os` functions which should be replaced with
`subprocess` calls like `os.popen` or `os.spawnv`

## FTP122
Find methods decorated with both `classmethod` and `property`.
Through the different python versions the behavior is unstable and should be avoided

## FTP123
Finds usage of `typing.Generator` where the last argument in the subscript is `None`,
because with PEP696 these can be omitted. The check is only active if

* running python 3.13+
* a `from __future__ import annotations` import is present in the module
* the current code is inside a `typing.TYPE_CHECKING` block

Also, the check will only consider type annotations (to prevent invalid syntax) if
at least one of the following conditions is true:

* python 3.12 or below is used
* the code is not inside a `typing.TYPE_CHECKING` block

## FTP124
Find assignments to `__all__` on non-module level, e.g. in classes or functions

## FTP125
Checks if the `typing.override` decorator is the first decorator applied to a function.
If descriptor based decorators like `@property` are present, too, `typing.override` should be the
seconds decorator applied.

See [here](https://peps.python.org/pep-0698/#limitations-of-setting-override) for details why the order matters

## FTP126
Checks if `typing.TypeAlias` is used.
With [PEP 695](https://peps.python.org/pep-0695/) the `type` statement should be used instead.
The check is only active for python 3.12 and onwards

## FTP127
Checks if `typing.TypeVar` is used.
With [PEP 695](https://peps.python.org/pep-0695/), `TypeVar`s are no longer needed.
The check is only active for python 3.12 and onwards

## FTP128
Checks if `typing.Generic` is used.
With [PEP 695](https://peps.python.org/pep-0695/), `Generic` is no longer needed.
The check is only active for python 3.12 and onwards

## FTP129
Checks if the cause of a raised error is the same as the caught error, e.g.

```python
except ValueError:
    raise MyError("some message") from ValueError
```

This is most likely a bug and should be replaced with

```python
except ValueError as err:
    raise MyError("some message") from err
```

## FTP130
Checks if `string.Template` is used with python 3.14 onwards.
Use t-strings (PEP 750) instead.

## FTP131
Checks if `re.compile` is called with a string constant within a
* function
* for loop
* while loop
* lambda

As the regex is recompiled each time the construct is called but won't change, it can be moved
to a constant on module level.

## FTP132
Checks if a module functions of ``re`` like ``re.fullmatch`` is called with a constant string
within a
* function
* for loop
* while loop
* lambda

As the regex is recompiled each time the construct is called but won't change, the pattern can be
compiled and stored in a constant and be used instead.

## FTP133
Checks `bz2`, `gzip`, `lzma` or `zlib` are imported without using the `compression` namespace.
With python3.14 these packages should be imported like `import compression.bz2` instead of
`import bz2`.
The check is only active for python 3.14 and onwards.

## FTP134
Checks if `isinstance` is called with a tuple which can be replaced with a union type.
For example `isinstance(foo, (str, int))` can be rewritten to `isinstance(foo, str|int)`.
The check is only active for python 3.10 and onwards.

## FTP135
Checks if `issubclass` is called with a tuple which can be replaced with a union type.
For example `issubclass(Foo, (A, B))` can be rewritten to `issubclass(Foo, A|B)`.
The check is only active for python 3.10 and onwards.

## FTP136
Checks if `type(None)` is used within `isinstance` when called with a union type.
For example `isinstance(foo, (str, type(None)))` can be rewritten to `isinstance(foo, str|None)`.

## FTP200
Find calls of `flask.abort` and `werkzeug.exceptions.abort`.
Instead of calling this helper function raise the appropriate exception directly

## FTP220
Find usage of `requests.codes` which should be replaced with `http.HTTPStatus`

## Docstyle
Rules to make docstrings PEP 257 compliant inspired by [pydocstyle](https://github.com/PyCQA/pydocstyle).
These rules are meant for projects which cannot or don't want to use ruff,, e.g. because flake8 is still used in parallel.

### FTP300
Checks if a public package has a docstring in it's `__init__` file.

### FTP301
Checks if a public class has a docstring.

### FTP302
Checks if a public method has a docstring.

### FTP303
Checks if a public function has a docstring.

### FTP304
Checks if a magic method (e.g. `__eq__`) has a docstring.
`__init__` methods are ignored

### FTP305
Checks if a `__init__` method has a docstring.

### FTP306
Checks if an overridden method (decorated with `typing.override`) has a docstring.

### FTP307
Checks if a public module has a docstring.

### FTP308
Checks if a docstring is completely empty.

### FTP309
Checks if the first line of a docstring is empty.
The first line is considered the summary.

### FTP310
Checks that in a multiline docstring the first line is followed by an empty line.

### FTP311
Checks if the first line ends with a period.

### FTP312
Checks that a function/method decorated with `typing.overload` has no docstring.

### FTP313
Checks if a magic function (e.g. module level `__getattr__`) has a docstring.

### FTP314
Checks that no empty line is present between a function/method docstring and the function body

### FTP315
Checks that the closing `"""` is on a separate line in a multiline docstring

### FTP316
Checks that a docstring starts with an uppercase letter or number unless the word is part of
`ftp-docstyle-lowercase-words`

### FTP317
Checks if triple quotes (`"""` or `'''`) are used for docstrings
