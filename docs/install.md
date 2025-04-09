# Installation

To start using flake8-tergeo, follow these steps:

**Install flake8-tergeo via pip**

```sh
pip install flake8-tergeo
```

**Configure flake8**:

In your `.flake8` configuration file, you need to enable the  flake8-tergeo extensions by adding `FT` to the `enable-extensions` option:

```ini
[flake8]
enable-extensions = FT
```

The set the `select` option to include `C` (`mccabe`), `E` (`pycodestyle`), `F` (`pyflakes`),
`W` (`pycodestyle`), and `FT` (`flake8-tergeo`) to ensure that only the necessary checks are executed:

```ini
[flake8]
select = C,E,F,W,FT
```
