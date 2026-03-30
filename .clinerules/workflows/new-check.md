# Create a New Check

This workflow guides you through creating a new flake8 check for the flake8-tergeo plugin.

## Step 1: Understand the Requirements

Ask the user what check to implement. Gather the following information:

- **Purpose**: What code pattern should be detected?
- **Examples of violations**: Code that should trigger the check
- **Examples of valid code**: Code that should NOT trigger the check
- **Suggested message**: What message should be shown to the user?

Make sure you fully understand the requirements. If you have open questions, proactively ask the user for clarification.

## Step 2: Determine the Check Group and Issue Number

The check codes follow the structure explained in `docs/checks.md`

To determine the next issue number:

1. Identify which group the check belongs to
2. Review `docs/checks.md` to find the last used code in that group
3. The new code should be the next increment

**Before continuing, confirm with the user:**
- Is the selected group appropriate?
- Is the issue number correct?

## Step 3: Prepare the Environment

Verify that the development environment is ready:

```bash
source .venv/bin/activate
uv sync --all-extras --all-groups
```

If the virtual environment does not exist or the sync command fails, ask the user how to proceed.

## Step 4: Implement the Check

Create or modify the appropriate check file in `_flake8_tergeo/checks/`.
The file to use depends on the AST node type being checked.

Follow the existing patterns in the codebase:

1. Use the `@register` decorator with the appropriate AST node type
2. Yield `Issue` objects with `line`, `column`, `issue_number`, and `message`
3. Keep the check function focused and well-documented

Example structure:

```python
@register(ast.SomeNode)
def check_something(node: ast.SomeNode) -> IssueGenerator:
    """Check for [description]."""
    if some_condition:
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="XXX",
            message="Description of the issue.",
        )
```

## Step 5: Write Tests

Create test files in the `tests/checks/` directory:

1. **Test data file**: Create `tests/checks/test_<module>/ftpXXX.txt` with:
   - Comments separating valid and invalid code sections
   - Code examples that should NOT trigger the check (valid code)
   - Code examples that SHOULD trigger the check (violations)

2. **Test function**: Add a test in `tests/checks/test_<module>.py`:

```python
FTPxxx = partial(
    Issue,
    issue_number="FTPxxx",
    message="Your error message here.",
)

def test_ftpxxx(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftpxxx.txt", issue_number="FTPxxx")
    assert results == [FTPxxx(line=X, column=Y), ...]
```

Run the tests to verify:

```bash
pytest tests/checks/test_<module>.py -k ftpxxx -v
```

## Step 6: Update Documentation

Add the new check to `docs/checks.md`:

1. Find the appropriate section based on the code range
2. Add an entry following the existing format:

```markdown
## FTPxxx
Description of what the check does.
Explain why this pattern is problematic.
Suggest the recommended alternative if applicable.
```

## Step 7: Add a Changelog Entry

Create a news fragment in the `news/` directory:

```bash
towncrier create +.feature
# the new file is echoed on teh console
echo "Added FTPxxx: Brief description of the check." > filename
```

## Step 8: Final Verification

Run the full linting:

```bash
# Run linting
pre-commit run --all-files
```

Ensure there are no linting errors before considering the implementation complete.
Note that if flake8 is executed, the new check is executed on the whole code base.
