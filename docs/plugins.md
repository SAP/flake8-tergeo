# Plugins

flake8-tergeo is a flake8 plugin that also includes other essential plugins and manages their execution and configuration.
This integration provides several benefits:

1. **Simplified Management**: Managing multiple flake8 plugins individually can be cumbersome,
    especially when dealing with different versions and configurations.
    flake8-tergeo simplifies this by including a curated list of important plugins with fixed versions,
    ensuring compatibility and reducing the overhead of manual management.
2. **Consistent Configuration**: flake8-tergeo can handle the configuration of the included plugins.
    All configuration values are prefixed with `ftp`.
    This ensures that all plugins are configured consistently, reducing the risk of
    misconfiguration and making it easier to maintain the code quality standards across the project.
3. **Unified Error Codes**: The error code prefixes of the included plugins are replaced with new ones,
    providing a unified and consistent error reporting system.
4. **Curated Plugin List**: The included plugin list is fixed and curated, meaning that only the
    most important and relevant plugins are included. This reduces the noise from less useful plugins
    and focuses on the most critical checks for your project.
5. **Resilience to Unmaintained Plugins**: If a plugin becomes unmaintained or certain checks are broken,
    flake8-tergeo can seamlessly replace them or provide fixes out of the box.
    This ensures continuous and reliable code quality checks without requiring manual intervention.

By using flake8-tergeo, users can benefit from a streamlined and efficient code quality
management process, ensuring that their code adheres to best practices with minimal effort.

## Plugin List

| ID | Plugin | Original Prefix | Description | Disabled Checks |
| --- | --- | --- | --- | --- |
| FTB | flake8-bugbear | B | Checks for common issues | 001, 016, 905 (if python <3.10), 950 |
| FTU | flake8-builtins | A | Checks for overwritten built-in methods | |
| FTC | flake8-comprehensions | C | Checks set/list/dict comprehensions | |
| FTT | flake8-pytest-style | PT | Checks common style issues or inconsistencies with pytest-based tests | 004, 005, 013, 019 |
| FTM | flake8-simplify | SIM | Checks for simplifications in your code | 116, 901 |
| FTY | flake8-typing-imports | TYP | Checks for incompatible use of the typing module for a defined python version | |
