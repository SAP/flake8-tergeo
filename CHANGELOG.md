# Changelog

<!-- towncrier release notes start -->

## 26.2.20.0 (2026-02-20)

### Features

- FTP139 which can find uses of `profile` and `cProfile` which should be replaced with
  `profiling.tracing` within python 3.15 onwards.

### Changes

- FTP108 now ignores usages of `NoReturn` in `Callable` like `x = Callable[[int], NoReturn]`
- If a module is not listed in ``--ftp-requirements-module-extra-mapping``, FTP041 will
  now only allow install requirements instead of all requirements
- Updated the release actions


## 26.1.28.0
- Support recursive optional requirements in FTP041

## 25.12.19.1
- Fixed an issue causing the plugin to fail with an internal error

## 25.12.19.0
- Dropped support for python 3.9
- FTP137 which can find mocks of `open`
- FTP045 will also find calls of `eval` and `exec`
- FTP121 will also find calls of `os.system`
- FTP138 which finds calls of trace functions like `sys.settrace`

## 25.10.9.0
- FTP077 now verifies also `isinstance` calls
- Corrected FTP019: its okay to call `OSError` with an `errno` constant as long as a 2nd argument
  is present

## 25.8.13.0
- FTP316 which checks that a docstring starts with an uppercase letter or number
- FTO317 which checks if triple quotes are used
- FTP134 which finds `isinstance` calls with tuples
- FTP135 which finds `issubclass` calls with tuples
- FTP136 which finds `type(None)` in `isinstance` calls using union types

## 25.7.9.0
- FTP314 which finds functions where docstrings and the function body are separated by an empty line
- FTP315 which finds multi-line docstrings where the closing `"""` is not on a separate line
- FTP3* checks will now also consider docstrings of private functions, packages, modules and classes
  but only if the docstring exists, meaning that missing docstrings are not reported

## 25.6.26.0
- Fixed an issue causing FTP303 to be reported on overloaded functions

## 25.6.25.0
- Support dependency groups in FTP041
- if ``ftp-auto-manage-options`` is true, the version given to flake8-typing-imports is adjusted if
  needed to a supported version
- New checks targeting docstring within the range of `FTP300-FT399`

## 25.6.11.0
- Support python 3.14
- Improve FTP097 to also consider `StrEnum` and `IntEnum`
- FTP133 which finds imports of compression modules without using the `compression` namespace if python 3.14 onwards is used
- FTP030 will report an import of `from __future__ import annotations` if python 3.14 onwards is used
- FTP003 and FTP007 will now consider all usages of the functions not only calls

## 25.5.22.0
- Support async for loops for all checks working on for loops
- FTP019 which finds `OSError` instantiations with `errno` constants
- FTP132 which finds usage of ``re`` functions with strings within functions
- Improve FTP131 to also consider loops and lambda statements

## 25.5.14.0
- Renamed `ftp-enforce-parens-in-return-single-element-tuple` to `ftp-disallow-parens-in-return-single-element-tuple`
- Support type aliases in FTP077 and FTP104
- Support `typing.Union` in FTP077 and FTP104
- FTP130 which finds usage of `string.Template`
- FTP131 which finds `re.compile` calls in functions

## 25.3.25.1

* Initial version
