# SoftReview Hub changelog

The latest entries appear first. Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

## 2026-11-23 · Public repository documentation review

- Limited the README to the project description, local setup, tests, and main files. Removed private integration and deployment details from the public documentation and kept verification outcomes here. Integration details are shared directly with the team.
- Documented pre-push checks, the same checks for shared material, and authorized service access in `AGENTS.md` and `SECURITY.md`. Expanded ignore rules for local course data, transfer archives, and the private integration guide.
- Audited tracked files and 15 commits reachable from the published branch and PR refs. Older revisions retain sensitive metadata and internal documentation. The affected locations are reported separately.
- Confirmed that the backend code and tests match the base revision. On Windows, 11 isolated tests passed and nine MySQL integration tests were skipped.

## 2026-11-23 · University Linux backend verification

- Recorded the team's manual SSH verification of backend commit `e31e10d0895a656f786417bbccc322be6195241a` in this entry and documented the result.
- Gunicorn started on the university Linux server. All eight HTTP read requests returned 200, and MySQL record counts matched expectations.
- The best and worst `price` rankings matched the expected averages calculated from the dataset.
- The evaluation write route returned 201. MySQL confirmed one new report and the four expected scores. The team removed the fictitious test records afterward.
- The team loaded anonymized data directly into MySQL for this backend verification. Verification of the Task 4 MongoDB import workflow remains pending because MongoDB authentication failed.

## 2026-11-23 · Windows verification and Linux handoff

- Locked the Linux Gunicorn dependency and added repeatable Windows, archive transfer, and university Linux checks to `README.md`.
- On Windows, `uv sync --locked --python 3.12` succeeded. `uv run --locked python -m unittest discover -s tests -v` passed 11 isolated tests with nine MySQL tests skipped. With isolated MySQL 8.0.36 enabled, all 20 tests passed. A fresh schema load produced 16 fictitious scores.
- Started Flask using the README command and verified HTTP 200 for eight read requests covering all read routes and ranking options, and HTTP 201 for a fictitious POST. The README shell examples passed syntax checks, the MySQL `SOURCE` sequence produced the expected fixture, and the staged Git archive contained exactly the 16 tracked files. Gunicorn and the assigned MySQL schema still need verification from the user's SSH terminal.

## 2026-11-23 · Criterion rankings

- Added the ranking route with validated options, parameterized filters, average scores, and a stable software ID tie-break. Added fictitious evaluations in `sql/test_data.sql` and documented the defaults and filter for the integration team.
- All 20 tests passed with Windows MySQL enabled. Fixtures verified both sort orders, the default criterion, known averages, a tie, a one-row limit, and product type filtering.
- Next, verify the Windows startup command and prepare the Linux handoff.

## 2026-11-23 · Transactional evaluation submission

- Implemented the evaluation write route in `app.py` using the agreed payload and one anonymous evaluator per submission. Documented the response and validation errors for the integration team.
- All 16 tests passed with Windows MySQL enabled. A valid submission added one evaluator, one report, and four verified scores. Invalid and unknown-software requests left counts unchanged. A temporary development trigger forced a failure during score insertion and all counts stayed unchanged after rollback.
- Next, implement rankings and verify both sort orders and the product type filter.

## 2026-11-23 · Table browsing and criteria

- Added the seven-table allowlist, explicit table projections, the criteria endpoint, and `sql/seed_criteria.sql`. Recorded the read contracts for the integration team.
- Applied the criteria script twice in isolated Windows MySQL. All 12 tests passed with MySQL enabled, including reads of every allowed table, rejection of an unknown table before connecting, and the four canonical criteria with their database IDs.
- Next, implement and verify the evaluation transaction.

## 2026-11-23 · Software catalog on MySQL

- Reused the seven-table course DDL in `sql/create_tables.sql`, added a fictitious catalog in `sql/test_data.sql`, and implemented the software catalogue route with controlled JSON errors in `app.py`.
- Loaded the DDL and fixture in the isolated Windows MySQL 8.0.36 database. All nine tests passed with MySQL enabled. A request over HTTP to Flask returned 200 and the four expected software rows.
- Next, expose the table allowlist and the four criteria.

## 2026-11-23 · MySQL connection and transaction handling

- Added `database.py`, MySQL Connector/Python, environment settings, and cursor and connection cleanup for reads and writes.
- Windows passed `uv sync --locked --python 3.12` and all four tests in `test_database.py`. A connector query confirmed access to the isolated `softreview_test` schema on MySQL 8.0.36.
- Next, load the course schema and fictitious data, then verify the software catalogue route.

## 2026-11-23 · Backend workflow and privacy rules

- Updated `AGENTS.md`, `SECURITY.md`, and `.gitignore` for incremental backend work and protection of local credentials, dumps, and raw data.
- Verified that the backend branch starts from the fetched `origin/main`. Checked representative paths with `git check-ignore` and confirmed `git ls-files --cached --ignored --exclude-standard` found no tracked ignored files. `.env.example` remains trackable.
- Next, connect Flask to an isolated Windows MySQL database and verify the software endpoint.

## 2026-11-23 · Health endpoint verified over HTTP

- Implemented the health check in `app.py` and marked it as available in `README.md`. The route works without a MySQL connection.
- Verified in Windows PowerShell that the health check returned HTTP 200 with the expected JSON when Flask ran locally with debug disabled.
- The tables, fictitious test data, remaining endpoints, and Linux deployment are pending.

## 2026-11-23 · Flask environment with uv

- Set up `pyproject.toml` and `uv.lock` with `uv add flask --python 3.12`. Added `.gitignore`, `.env.example`, and documentation for the planned MySQL environment variables in `README.md`.
- On Windows, `uv sync --locked --python 3.12` completed successfully. `uv run --locked python --version` and `uv run --locked flask --version` confirmed Python 3.12.16, Flask 3.1.3, and Werkzeug 3.1.9.
- `git check-ignore` confirmed that `.env`, `.env.local`, `.venv/`, `project.json`, and `dumps/local.sql` are ignored and that `.env.example` can be tracked.

## 2026-11-23 · Initial documentation

- Documented the scope, team workflow, API contract, and repository rules in `AGENTS.md`, `SECURITY.md`, `README.md`, and this changelog.
- Verified locally with `git status --short --branch`, `git remote -v`, and `git log -5 --oneline` that the clone was on `main`, with no working files or commits, and that `origin` pointed to `https://github.com/SMUAlfredo/softreview-hub.git`.
- Reviewed `create_tables.sql`, `create_db.sh`, and `data2mongo2sql.sh` outside the clone. The DDL defines the seven tables without selecting a database. The scripts generate `CREATE DATABASE IF NOT EXISTS` and `USE` using the supplied database name. The reviewed copy of `data2mongo2sql.sh` ends after table creation. The full import workflow still needed verification.

## Course project scope

- Task 4 imports the software records through MongoDB and MySQL. The import replaces evaluator email addresses with anonymous IDs and excludes profile records. The course source data stays outside Git. The Task 3b and Task 4 submission scripts are maintained separately from the application.
- Task 5 demonstrates table browsing, transactional evaluation submission, and ranking by criterion.
- Task 6 includes a presentation and a short report on the application structure. Team responsibilities cover the backend, frontend, and integration and reporting.

## Before this stage · Infrastructure checks reported by the team

- The team tested Python 3.12.3, uv, Flask, MySQL Connector/Python, and Gunicorn on the Linux server. They confirmed HTTP access through an SSH tunnel and local MySQL access using the assigned MySQL account and database. The existing tables were preserved.
- Those checks covered the infrastructure. Implementing the application and verifying its first route over HTTP were still pending.
