# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**docuFetch** is a Python project. The repository is in early stages — no source code has been committed yet.

## Python Environment

The `.gitignore` is configured for Python with support for common tooling:

- **Virtual environments:** `.venv`, `venv/`, `env/` (standard `venv` or `uv`)
- **Package managers:** pip, pipenv, poetry, pdm, uv, pixi
- **Linting/typing:** ruff (`.ruff_cache/`), mypy, pytype, pyre
- **Testing:** pytest (`.pytest_cache/`), tox, coverage

Once the project is set up, typical commands will likely follow these patterns:

```bash
# Install dependencies
pip install -r requirements.txt
# or: uv sync / poetry install

# Run tests
pytest

# Run a single test
pytest tests/path/to/test_file.py::test_name

# Lint
ruff check .
ruff format .
```

Update this file once the project structure is established.
