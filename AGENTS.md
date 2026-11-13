# AGENTS.md — Repository Agent Instructions (Source of Truth)

This file defines the canonical coding directives for this repository.

If other instruction files exist (Copilot, IDE rules, contributor docs) and conflict with this file, follow this file and treat the others as stale.


## Table of contents

- [Project basics](#project-basics)
- [How to run code](#how-to-run-code)
- [Coding directives (Python)](#coding-directives-python)
- [Django architecture conventions](#django-architecture-conventions)
- [Front-end change guidance](#front-end-change-guidance)
- [Tests](#tests)
- [Change workflow expectations](#change-workflow-expectations)
- [If instructions are missing or ambiguous](#if-instructions-are-missing-or-ambiguous)
- [Agent project index](#agent-project-index)


## Project basics

- Primary language: Python
- Target runtime: Python 3.8.10, as pinned in `pyproject.toml`
- Dependency / execution tool: `uv`
- Project-root is the directory containing this file (and `.git/`, and `.gitignore`).
- NEVER include full server filesystem paths in documentation, examples, or agent notes. Use relative paths or variable names instead.
- Keep all server-deployment documentation outside READMEs, including any mention of deployment caller scripts. Creating the caller outside the Git repository remains part of tomlization.


## How to run code

- Assume user is in the project-root directory.
- Do not use `python` to run scripts.
- Run a script via: `uv run ./path_to_script.py --help`
- Run tests via:
    - `uv run ./run_tests.py`
        - Note that `run_tests.py` has usage instructions about how to run more granular tests.
- Run django management scripts via: `uv run ./manage.py THE-COMMAND`


## Coding directives (Python)

### Type hints and imports

- Use Python 3.8-compatible type hints for functions and important variables.
- Use `typing.List`, `typing.Dict`, and `typing.Optional` when needed; newer generic and union syntax is unavailable on the pinned interpreter.
- Prefer simple annotations and explicit checks for `None` or an expected type.

### Script structure

- Structure runnable modules as:
  - `def main() -> None: ...`
  - `if __name__ == '__main__': main()`
- Keep `main()` simple: parse args / orchestrate calls only.
- Put real logic into top-level helper functions and modules (no nested function definitions).
- Rarely use more than three levels of hierarchy: main() can call helper_A() which can call helper(B) which can, if necessary, can call helper(C) -- but that's it.

### Functions and control flow

- Prefer single-return functions (use local variables and a final return).
- Do not define functions inside other functions.
- Favor clarity and explicitness over cleverness.

### Logging

- When adding a log statement, when possible, format variable values as a label, followed by a comma and a space, with the value enclosed in double backticks.
- Prefer a label that matches the variable name. For example: ```log.debug(f'branch_and_commit, ``{branch_and_commit}``')```

### HTTP and networking

- Use `httpx` for all HTTP calls.
- Do not introduce alternate HTTP libraries (e.g., `requests`, `aiohttp`) unless the repository already depends on them and there is a documented reason.

### Docstrings

- Use triple-quoted docstrings.
- Write docstrings in present tense, with triple-quotes on their own lines.
  - Good:
    ```
    """
    Parses ...
    """
    ```
  - Avoid: `"""Parse ..."""`
- The last line of non-test function-docstrings should be: `Called by: the_caller_function()` (or, if in another class/module, `Called by: module.Class.the_caller_function()`)
- Start test-function docstring-text with "Checks..."
- For header-comments, in functions, start the comment with two hashes (e.g., `## does this`).

### Additional coding directives

- inspect `ruff.toml` for additional coding directives, such as `max-line-length` and `quote-style`.

### Markdown formatting

- Do not use hard line-breaks in markdown files; let paragraphs wrap naturally.
- When creating a Markdown file with more than three top-level `##` headings, add a table of contents near the top with links to those `##` headings.


## Django architecture conventions

### View-layer responsibilities

- `project/app/views.py` should contain **only** view functions that directly handle URL endpoints.
- Every view function in `project/app/views.py` should correspond to an entry in `project/config/urls.py`.
- Views should act as **manager/orchestrator** functions:
  - Parse request input (query params, POST body, files)
  - Perform minimal validation and shaping of inputs
  - Delegate substantive work to modules under `project/app/lib/`
  - Convert returned results into the appropriate `HttpResponse` (HTML, JSON, redirects)

### Business logic placement

- Put domain logic, integrations, and reusable operations in `project/app/lib/` (not in `views.py`).
- If multiple endpoints share logic, move that shared logic into `project/app/lib/` and keep each view thin.
- Prefer pure, testable functions in `project/app/lib/` that accept plain Python values (not Django request objects)
  unless passing the request is necessary for a narrow, well-justified reason.

### Imports and dependencies

- `views.py` should primarily import:
  - Django primitives (`HttpRequest`, `HttpResponse`, `render`, `redirect`, etc.)
  - The minimal set of functions/classes from `project/app/lib/` needed for each endpoint
- Avoid creating a secondary abstraction layer inside `views.py` (no view-helper utilities); place helpers in `project/app/lib/`.


## Front-end change guidance

- When front-end changes are required, use JavaScript only where it is truly required.
- Prefer updates in CSS, Python code, or Django template code when those can satisfy the behavior or presentation need.


## Tests

- Use the standard library `unittest` framework (not pytest) for non-Django projects.
- Use Django's test framework for Django projects.
- New behavior should usually come with a focused test covering:
  - the happy path
  - at least one failure / edge case


## Change workflow expectations

When implementing a change (especially from an issue/task):

1. Read relevant surrounding code and match existing conventions.
2. Make the smallest correct change that satisfies the request.
3. Update tests and run: `uv run ./run_tests.py`
4. If you cannot run tests in your environment, still write/adjust tests and state what you would run.

### Commit messages

- Group related files into logical, focused commits; do not require a separate commit for every file.
- Keep each commit message brief, with no more than ten words.
- Write messages in the present tense so they complete the phrase "This commit..." Begin with a fitting verb such as "Adds," "Implements," or "Updates."


## If instructions are missing or ambiguous

- Do not ask questions unless absolutely necessary to proceed.
- Make reasonable assumptions, state them explicitly, then implement.
- If blocked, provide:
  - what you tried
  - what you found in the repo
  - a concrete next step (command, file to edit, or minimal decision needed)


## Agent project index

- `manage.py` runs management commands; `run_tests.py` supplies synthetic settings and temporary storage before running Django tests.
- `config/settings.py` loads `../.env` relative to its own location. File values override inherited environment values; interpolation is disabled.
- `config/testing.py` sets all required test values and disables `.env` loading. Both test entry points use it.
- `config/urls.py` maps upload, information, version, and error-check views in `reserves_uploader_app/views.py`.
- `reserves_uploader_app/forms.py` validates uploaded filenames; `lib/uploader_helper.py` saves files and fetches cached header HTML with requests.
- `reserves_uploader_app/lib/pather.py` normalizes Unicode and builds filename-based subdirectories and public links.
- `reserves_uploader_app/lib/version_helper.py` uses Trio to run Git commands for the version view.
- Sessions use files. No application database is configured. Preserve the MySQL driver in the environment groups until its wider use has been reviewed.
- Keep exact initial dependency pins; see the README dependency inventory before any later cleanup.
- Validate changed Python files with the project interpreter and basic Pylance or Pyright checks. Run Ruff from this directory using `ruff.toml`.
