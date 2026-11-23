# Codex instructions for SoftReview Hub

At the start of each session, read `SECURITY.md`, the latest entry in `UPDATE.md`, and `README.md`, in that order. Then review `git status --short --branch`, the recent commits, `pyproject.toml`, and `uv.lock`. For the task at hand, review any relevant code, SQL, and tests. Respect the team's changes and commits.

- Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.
- Make small changes, use clear names, and keep Flask routes simple. Reuse the existing structure.
- Validate inputs in Flask. Parameterize query values and use allowlists for SQL identifiers and sort options. Group related writes in a transaction.
- Preserve the API contract agreed with the frontend team. Confirm how anonymous evaluator IDs are assigned before implementing the POST, and agree on any new ranking parameters before adding them.
- Create one local commit per logical change. Verify the change, add its entry to `UPDATE.md` in the same commit, and review the staged diff before committing. Include only the files related to the change and preserve the existing history and work. Push only when the user asks.

The team uses `main` as the stable branch, `frontend` for UI development, and `integration` to bring the components together and test them.
