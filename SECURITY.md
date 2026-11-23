# SoftReview Hub security

Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

## Credentials and data

- Configure the connection through environment variables. Use `.env.example` as a template with placeholder values and keep the local `.env` file out of Git.
- Keep private keys, dumps, and files containing personal data, including the original dataset, out of Git. Use fictitious test data. MySQL and the API handle only anonymous evaluator IDs.
- Inspect tracked paths as well as ignore rules before pushing. If a secret is found, identify only its file or variable, stop the affected push, and correct the exposure. If it reached the remote, notify the owner so they can rotate it.
- Keep secrets, queries, and stack traces out of HTTP responses. Keep credentials and personal data out of logs, examples, documentation, and shared commands. Error messages should explain the problem and, when applicable, how to fix it.

## Queries and the shared server

- Parameterize SQL values. In `/api/tables/<name>`, resolve the requested name through an explicit mapping of the seven project tables (`Brand`, `ProductType`, `SoftwareSystem`, `Evaluator`, `EvaluationReport`, `ScoreCriterion`, and `EvaluationScore`). Use allowlists for any option that selects a SQL identifier or the ranking order.
- Validate in Flask that the four scores are integers between 1 and 10. Save the report and its scores in a single InnoDB transaction.
- Close cursors and connections after each operation, including failures. Return API errors using the agreed JSON format.
- Limit server operations to the assigned account, the `u07` database, and the assigned directories. Use the minimum privileges available. Before running existing SQL, review `CREATE DATABASE`, `USE`, and `DROP` statements and confirm the target database.
- For remote testing, use only the authorized interfaces for Flask, Gunicorn, and MySQL. Access HTTP through the agreed SSH tunnel and keep debug mode disabled. Coordinate any public access or server configuration changes with the university.
- Use an isolated development database on Windows and bind Gunicorn to localhost on Linux. Inspect the existing schema in `u07` before running any DDL and preserve existing tables and data.

## If a secret is exposed

Revoke or rotate the exposed credential or key immediately. Notify the team and, if university resources are affected, the server administrator or university IT support. If personal data is involved, also follow the university's reporting process. Identify where the secret was shared, remove it from those locations, and coordinate any Git history cleanup with the team. Revocation or rotation is required even after the secret is removed from a file.
