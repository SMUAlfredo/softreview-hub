# SoftReview Hub security

Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

## Credentials and data

- Configure the connection through environment variables. Use `.env.example` as a template with placeholder values and keep the local `.env` file out of Git.
- Keep private keys, dumps, and files containing personal data, including the original dataset, out of Git. Use fictitious test data. MySQL and the API handle only anonymous evaluator IDs.
- Inspect tracked paths as well as ignore rules before pushing. If a secret is found, identify only its file or variable, stop the affected push, and correct the exposure. If it reached the remote, notify the owner so they can rotate it.
- Keep secrets, queries, and stack traces out of HTTP responses. Keep credentials, course data, and assigned infrastructure identifiers out of logs, public documentation, and shared examples. Error messages should explain the problem and, when applicable, how to fix it.

## Queries and local development

- Parameterize SQL values. Resolve table names through an explicit mapping of the project tables. Use allowlists for any option that selects a SQL identifier or the ranking order.
- Validate evaluation inputs in Flask and save each submission in a single InnoDB transaction.
- Close cursors and connections after each operation, including failures. Return API errors using the agreed JSON format.
- Use an isolated local MySQL database and an account with the minimum privileges needed. Before running existing SQL, review `CREATE DATABASE`, `USE`, and `DROP` statements and confirm the target database.
- Keep the API and its database connection on `127.0.0.1`. Keep Flask debug mode disabled.

## Public repository and API access

- Treat tracked files, Git refs, PRs, issues, screenshots, and artifacts as public. Keep credentials, private keys, personal email addresses, course data, assigned accounts, internal addresses, and private API and deployment documentation out of all of them. Share integration details through the team's approved private channel. Public examples use fictitious data and placeholders.
- Before each push, review tracked filenames, file contents, and the full outgoing diff, including committed changes. Apply the same review before sharing a PR, issue, screenshot, or artifact. Use your GitHub noreply address for commit authorship. Check the history if there is evidence of an earlier exposure and report only the information type and affected location.
- Run development and demos locally.
- Treat source code in this public repository as readable by anyone. If route definitions must remain confidential, keep the implementation in a private repository or private source control. Access controls protect the running service.

## If a secret is exposed

Revoke or rotate the exposed credential or key immediately. Notify the team and, if university resources are affected, the server administrator or university IT support. If personal data is involved, also follow the university's reporting process. Identify where the secret was shared, remove it from those locations, and coordinate any Git history cleanup with the team. Revocation or rotation is required even after the secret is removed from a file.
