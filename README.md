[![REUSE status](https://api.reuse.software/badge/github.com/SAP/flake8-tergeo)](https://api.reuse.software/info/github.com/SAP/flake8-tergeo)
[![Coverage Status](https://coveralls.io/repos/github/SAP/flake8-tergeo/badge.svg)](https://coveralls.io/github/SAP/flake8-tergeo)

# flake8-tergeo

## About this project

flake8-tergeo is a flake8 plugin which adds many new rules to improve your code quality.
Out of the box it also brings a curated lists of other plugins without additional efforts needed.
In difference to other projects, the list of included plugins is rather small and actively maintained.

The included plugins and checks are opinionated, meaning that e.g. f-strings are preferred.
Therefore, checks to find other formatting methods are included but none, to find f-strings.

Also, code formatters like ``black`` and ``isort`` are recommended; therefore no code
formatting rules are included.

## Documentation

You can find the documentation [here](https://sap.github.io/flake8-tergeo/).

## Release Actions
* Determine the new version by using the format `YY.M.D.C` with `YY` are the two last digits of the
  year, `M` is the current month (maybe two digits if needed), `D` is the current day (maybe two digits if needed)
  and `C` is a counter of the releases per day starting at 0
* Rename the section `Next version` in the [CHANGELOG](CHANGELOG.md) to the version released
  and create a new empty one
* Push a new tag like X.X.X to trigger the release

## Support, Feedback, Contributing

This project is open to feature requests/suggestions, bug reports etc. via [GitHub issues](https://github.com/SAP/flake8-tergeo/issues). Contribution and feedback are encouraged and always welcome. For more information about how to contribute, the project structure, as well as additional contribution information, see our [Contribution Guidelines](CONTRIBUTING.md).

## Security / Disclosure
If you find any bug that may be a security problem, please follow our instructions at [in our security policy](https://github.com/SAP/flake8-tergeo/security/policy) on how to report it. Please do not create GitHub issues for security-related doubts or problems.

## Code of Conduct

We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone. By participating in this project, you agree to abide by its [Code of Conduct](https://github.com/SAP/.github/blob/main/CODE_OF_CONDUCT.md) at all times.

## Licensing

Copyright 2025 SAP SE or an SAP affiliate company and flake8-tergeo contributors. Please see our [LICENSE](LICENSE) for copyright and license information. Detailed information including third-party components and their licensing/copyright information is available [via the REUSE tool](https://api.reuse.software/info/github.com/SAP/flake8-tergeo).
