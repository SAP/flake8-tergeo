# Changelog

## Next version

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
