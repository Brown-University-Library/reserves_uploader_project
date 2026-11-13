# Reserves uploader

Allows staff to upload PDFs for [Leganto](https://exlibrisgroup.com/products/leganto-reading-list-management-system/). Files are spread across subdirectories based on their names: `1234567890.pdf` is saved as `12/34/1234567890.pdf` beneath the configured upload directory. This keeps large collections out of a single directory.

## Contents

- [More information](#more-information)
- [Local setup](#local-setup)
- [Usage](#usage)
- [Tests](#tests)
- [Primary dependencies](#primary-dependencies)

## More information

The application uses file-based sessions and does not configure a database. `reserves_uploader_app/lib/pather.py` builds file paths and public links. `reserves_uploader_app/lib/uploader_helper.py` writes uploads, adds a timestamp when a filename already exists, and retrieves cached header HTML.

`pyproject.toml` pins the Python and package versions. `uv.lock` records the resolved packages. Use uv for setup and dependency management.

## Local setup

Run these commands from the repository directory with [uv](https://docs.astral.sh/uv/) available:

```bash
uv sync --locked --group local
cp -n .env.example ../.env
mkdir -p ../local_data/sessions ../local_data/static ../local_data/uploads
```

`cp -n` preserves an existing `.env`. Review `../.env` before starting the app. The example uses directories beneath `../local_data`; an existing settings file may use different directories, which must already exist and be writable.

Both management commands and WSGI load `.env` from the outer directory, based on the location of `config/settings.py`. Values in that file override inherited environment values. Variable interpolation is disabled, so text such as `${NAME}` stays literal. Relative filesystem settings are resolved from the outer directory. Keep the real `.env` outside Git.

For the example settings, create a small local header file if it does not already exist:

```bash
if [ ! -e ../local_data/uploads/header.html ]; then
    printf '%s\n' '<header>Local reserves uploader</header>' > ../local_data/uploads/header.html
fi
```

In another terminal, from the repository directory, serve the sample header and uploaded files:

```bash
uv run python -m http.server 8001 --bind 127.0.0.1 --directory ../local_data/uploads
```

This local file server lets the default example load its header and open uploaded-file links. An existing `.env` may instead point to other services.

## Usage

```bash
uv run ./manage.py check
uv run ./manage.py runserver
```

Open [the local uploader](http://127.0.0.1:8000/uploader/), choose a file, and upload it. The page displays a link to the saved file. `/version/` displays Git branch and commit information.

## Tests

```bash
uv run ./run_tests.py
uv run ./run_tests.py reserves_uploader_app.tests.PathsTest -v 2
```

The runner supplies synthetic settings and temporary upload, session, and log locations. It prevents settings from opening the real `.env`. `uv run ./manage.py test` uses the same isolation. Tests cover filenames, directory creation, uploads with repeated filenames, the version view, and settings loading; external header requests are replaced with sample HTML during tests.

## Primary dependencies

This inventory uses the original dependency declarations preserved in Git history, current imports and configured features, and dependency relationships in `uv.lock`.

| Package | Purpose and usage |
| --- | --- |
| Django | Views, forms, templates, file sessions, and the test framework; configured in `config/settings.py` and imported throughout `reserves_uploader_app/`. |
| requests | Fetches header HTML in `reserves_uploader_app/lib/uploader_helper.py`. It remains in use at its existing version. |
| trio | Runs Git subprocesses for the version view in `reserves_uploader_app/lib/version_helper.py`. |
| python-dotenv | Loads the outer `.env` in `config/settings.py`; replaces the old `shellvars-py` loading code. Version 1.0.1 supports the pinned interpreter. |

The first conversion used exact `==` versions from the installed application packages, including their supporting packages. Certifi has since been updated to `2026.10.23`; the other initial pins remain unchanged. Django brings `asgiref`, `pytz`, and `sqlparse`; requests brings `certifi`, `charset-normalizer`, `idna`, and `urllib3`; Trio brings `async-generator`, `attrs`, `exceptiongroup`, `idna`, `outcome`, `sniffio`, and `sortedcontainers`. The lockfile also includes Trio's Windows-only `cffi` dependency and its `pycparser` dependency; these are not installed on macOS or Linux.

The `local` group needs no extra packages. The `staging` and `prod` groups retain `mysqlclient==2.1.1` from the environment snapshots. It requires compatible MySQL or MariaDB development libraries and a compiler when no wheel is available. No database is configured by the application, so its continuing need should be reviewed separately before removing it. PyMySQL appeared in the former local dependency declarations, but is absent from both snapshots and has no confirmed application use; it has not been carried forward.

Tests use Django and the standard library. Ruff and Pyright are separate checking tools, not application dependencies. The former pip-tools workflow and its build tooling are no longer needed for dependency management. `pip`, `setuptools`, and `wheel` are not declared as runtime dependencies. The former `shellvars-py` dependency is superseded by python-dotenv.

After sustained confirmation that the converted application works normally:

- Review a separate Python and dependency upgrade.
- Reduce the main dependency list to packages the application needs directly, preserving any runtime support packages and environment groups that remain necessary.
- Use the preferred `package~=1.2.0` notation with patch zero for those future declarations, while keeping exact resolved versions in `uv.lock`.
- Review any Git commit pins separately and check each relevant dependency group again.
