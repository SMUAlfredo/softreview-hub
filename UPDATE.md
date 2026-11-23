# SoftReview Hub changelog

The latest entries appear first. Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

## 2026-11-23 · Initial documentation

- Documented the scope, team workflow, API contract, and repository rules in `AGENTS.md`, `SECURITY.md`, `README.md`, and this changelog.
- Verified locally with `git status --short --branch`, `git remote -v`, and `git log -5 --oneline` that the clone was on `main`, with no working files or commits, and that `origin` pointed to `https://github.com/SMUAlfredo/softreview-hub.git`.
- Reviewed `create_tables.sql`, `create_db.sh`, and `data2mongo2sql.sh` outside the clone. The DDL defines the seven tables without selecting a database. The scripts generate `CREATE DATABASE IF NOT EXISTS` and `USE` using the supplied database name. The reviewed copy of `data2mongo2sql.sh` ends after table creation. The full import workflow still needed verification.

## Before this stage · Infrastructure checks reported by the team

- The team tested Python 3.12.3, uv, Flask, MySQL Connector/Python, and Gunicorn on the Linux server. They confirmed HTTP access through an SSH tunnel and local MySQL access using the `u07` account and its permissions on the `u07` database. The existing tables were preserved.
- Those checks covered the infrastructure. Implementing the application and verifying its first route over HTTP were still pending.
