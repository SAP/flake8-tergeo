# Configuration

## Global Configuration

* `ftp-python-version`: used for checks depending on a python version, e.g. if a certain feature
  is enabled or not. By default the current python interpreter version

## Auto-manage Configuration

If `ftp-auto-manage-options` is enabled, certain options of wrapped flake8 plugins are automatically
set to new default values if they are not specified via the flake8 command line or configuration file.
Please note that the list of these options and their default values may change between minor versions.
The default setting is false.

If enabled, the following options are automatically managed:

* `ftp-min-python-version` (by `flake8-typing-imports`): this options specified the minimum python
  version supported or used by the project. It is set to the same value as `ftp-python-version`

## Developer Comments
Developer comments are comments such as *TODO xxx* or *FIXME later*.

With these options it is possible to enforce certain style rules for these comments, such as:
* disallow certain identifier like *FIXME*
* enforce identifier to a tracking system like jira (e.g. `SOME-123 TODO this needs to be done`)
* enforce a description

Please note, that the check is case-insensitive, meaning that all dev comment identifier, comments and
project ids are converted to uppercase for comparison.

* `ftp-dev-comments-tracking-project-ids`: defines the tracking projects which must be present in a dev comment.
  If the configuration is not set, the check will not be executed. By default an empty list
* `ftp-dev-comments-allowed-synonyms`: List of valid dev comment identifiers. The default value is *TODO*
* `ftp-dev-comments-disallowed-synonyms`: List of invalid dev comment identifier. Defaults to *FIXME*
* `ftp-dev-comments-enforce-description`: Checks if after the dev comment identifier (and optionally after
  the tracking project id) additional text is present. By default false


## Requirements check
Check if a library is imported but not specified as a requirement.
This check only works with projects installed in their environment, meaning that projects not using
setuptools or poetry but pure requirement.txt files are not supported.

This check is not active if the configuration `ftp-distribution-name` is not set.

The check will go through all import statements and check if it's listed as a requirement.
Most projects will use packages which are not part of the requirements. e.g. `my-project` uses
the packages `my_project` and in it's test code `tests`.
These need to be specified inside the configuration `ftp-distribution-name`.

Also not always does the package match the distribution name, e.g. `git` is distributed as
`gitpython`.
In this case the configuration `ftp-requirements-mapping` allows to specify a mapping.
When namespace packages like `opentelemetry` are used, the packages are split over multiple
distributions.
The mapping of `ftp-requirements-mapping` can consume nested packages as it's key.
For instance, `ftp-requirements-mapping` could be written as
`ftp-requirements-mapping = opentelemetry.trace:opentelemetry-api,opentelemetry.sdk:opentelemetry-sdk`.

With the above the matching algorithm is as followed:

1. Transform the import/import-from statement to a string (`from foo.bar import baz` -> `foo.bar.baz`)
1. Check if the package starts any mapping key of `ftp-requirements-mapping`
1. If yes, use the mapped distribution name
1. If not extract the first part (`foo.bar` -> `foo`) and use it as the distribution name
1. Check if the distribution name is part of the project requirements, a stdlib module or listed
   in `ftp-requirements-packages`

Please note, that these checks base on the current working directory to map the current analysed file
to a module name.
Therefore, always execute `flake8` in the projects root folder, else the behavior and findings
of this check is not defined.
Also, if files are given directly to the flake8 command, the path should be relative to the
projects root folder.

* `ftp-distribution-name`: name of the project
* `ftp-requirements-packages`: comma-separated list of the packages defined by this project
  (e.g. `tests` and `my_package`)
* `ftp-requirements-mapping`: a comma-separated list of mappings between the packages and distributable names
* `ftp-requirements-ignore-type-checking-block`: if set to true, the check will ignore type checking
  blocks (`typing.TYPE_CHECKING`)
* `ftp-requirements-module-extra-mapping`: comma separate list of mappings in the format
  `<module> | extra [extra]`. Each mapping defines, that the given modules and all submodules
  are allowed to use the requirements specified in the extras.
  The module name can also limit itself to a function or class inside the module,
  e.g. for a class `A` with a method `foo` in the module `mod` the mapping would be `mod::A::foo`.
  If multiples module names match to the file under check, the extra lists are combined.
  If the option is not set, all modules can import all requirements from all extras
