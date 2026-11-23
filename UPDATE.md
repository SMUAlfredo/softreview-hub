# SoftReview Hub changelog

The latest entries appear first. Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

## 2026-11-23 · Transactional evaluation submission

- Implemented `POST /api/evaluations` in `app.py` using the agreed payload and one anonymous evaluator per submission. Documented the 201 response and validation errors in `README.md`.
- All 16 tests passed with Windows MySQL enabled. A valid submission added one evaluator, one report, and four verified scores. Invalid and unknown-software requests left counts unchanged. A temporary development trigger forced a failure during score insertion and all counts stayed unchanged after rollback.
- Next, implement rankings and verify both sort orders and the product type filter.

## 2026-11-23 · Table browsing and criteria

- Added the seven-table allowlist, explicit table projections, the criteria endpoint, and `sql/seed_criteria.sql`. Recorded the read contracts in `README.md`.
- Applied the criteria script twice in isolated Windows MySQL. All 12 tests passed with MySQL enabled, including reads of every allowed table, rejection of an unknown table before connecting, and the four canonical criteria with their database IDs.
- Next, implement and verify the evaluation transaction.

## 2026-11-23 · Software catalog on MySQL

- Reused the seven-table course DDL in `sql/create_tables.sql`, added a fictitious catalog in `sql/test_data.sql`, and implemented `GET /api/software` with controlled JSON errors in `app.py`.
- Loaded the DDL and fixture in the isolated Windows MySQL 8.0.36 database. All nine tests passed with MySQL enabled. A request over HTTP to Flask returned 200 and the four expected software rows.
- Next, expose the table allowlist and the four criteria.

## 2026-11-23 · MySQL connection and transaction handling

- Added `database.py`, MySQL Connector/Python, environment settings, and cursor and connection cleanup for reads and writes.
- Windows passed `uv sync --locked --python 3.12` and all four tests in `test_database.py`. A connector query confirmed access to the isolated `softreview_test` schema on MySQL 8.0.36.
- Next, load the course schema and fictitious data, then verify `GET /api/software`.

## 2026-11-23 · Backend workflow and privacy rules

- Updated `AGENTS.md`, `SECURITY.md`, and `.gitignore` for incremental backend work and protection of local credentials, dumps, and raw data.
- Verified that the backend branch starts from the fetched `origin/main`. Checked representative paths with `git check-ignore` and confirmed `git ls-files --cached --ignored --exclude-standard` found no tracked ignored files. `.env.example` remains trackable.
- Next, connect Flask to an isolated Windows MySQL database and verify the software endpoint.

## 2026-11-23 · Health endpoint verified over HTTP

- Implemented `GET /health` in `app.py` and marked it as available in `README.md`. The route works without a MySQL connection.
- In Windows PowerShell, started the app with `uv run --locked flask --app app run --host 127.0.0.1 --port 5000` with debug mode disabled. From a second terminal, `curl.exe --silent --show-error --max-time 5 -i http://127.0.0.1:5000/health` returned `HTTP/1.1 200 OK`, `Content-Type: application/json`, and `{"data":{"status":"ok"},"success":true}`. Verified the status code and the JSON response body.
- The tables, fictitious test data, remaining endpoints, and Linux deployment are pending.

## 2026-11-23 · Flask environment with uv

- Set up `pyproject.toml` and `uv.lock` with `uv add flask --python 3.12`. Added `.gitignore`, `.env.example`, and documentation for the planned MySQL environment variables in `README.md`.
- On Windows, `uv sync --locked --python 3.12` completed successfully. `uv run --locked python --version` and `uv run --locked flask --version` confirmed Python 3.12.16, Flask 3.1.3, and Werkzeug 3.1.9.
- `git check-ignore` confirmed that `.env`, `.env.local`, `.venv/`, `project.json`, and `dumps/local.sql` are ignored and that `.env.example` can be tracked.

## 2026-11-23 · Initial documentation

- Documented the scope, team workflow, API contract, and repository rules in `AGENTS.md`, `SECURITY.md`, `README.md`, and this changelog.
- Verified locally with `git status --short --branch`, `git remote -v`, and `git log -5 --oneline` that the clone was on `main`, with no working files or commits, and that `origin` pointed to `https://github.com/SMUAlfredo/softreview-hub.git`.
- Reviewed `create_tables.sql`, `create_db.sh`, and `data2mongo2sql.sh` outside the clone. The DDL defines the seven tables without selecting a database. The scripts generate `CREATE DATABASE IF NOT EXISTS` and `USE` using the supplied database name. The reviewed copy of `data2mongo2sql.sh` ends after table creation. The full import workflow still needed verification.

## Before this stage · Infrastructure checks reported by the team

- The team tested Python 3.12.3, uv, Flask, MySQL Connector/Python, and Gunicorn on the Linux server. They confirmed HTTP access through an SSH tunnel and local MySQL access using the `u07` account and its permissions on the `u07` database. The existing tables were preserved.
- Those checks covered the infrastructure. Implementing the application and verifying its first route over HTTP were still pending.
