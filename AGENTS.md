# Codex instructions for SoftReview Hub

Start with this file and the latest entries in `UPDATE.md`. Use the changelog to find completed work, verification results, pending steps, and relevant files. Compare it with `git status --short --branch` and newer commits, then consult `SECURITY.md` and the relevant sections of the README, course specification, code, SQL, and tests. Review `pyproject.toml` and `uv.lock` for Python changes. After an interruption, check the working tree, local commits, and remote branch before repeating work.

- Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.
- Make the smallest change that meets the requirement. Reuse existing logic, use clear names, give each function one responsibility, and add dependencies for current needs.
- Remove unused imports, duplicate or unreachable code, and temporary files from the current task. Before deleting a function, dependency, or file, check Flask entry points, scripts, tests, configuration, and README commands for references. Preserve course submission scripts and teammates' work.
- Search for the files and symbols relevant to the task. Run the affected checks after each increment and the relevant suite at the end. Write documentation, comments, and commit messages in English.
- Validate inputs in Flask. Parameterize query values and use allowlists for SQL identifiers and sort options. Group related writes in a transaction.
- Preserve the API contract agreed with the frontend team. Document decisions for open details with examples and keep the agreed POST fields and ranking URLs compatible.
- Make one commit per verified increment. Record the change, files, actual checks, and any remaining work in `UPDATE.md`. Stage only files from the increment and review the staged names and diff for unrelated work and sensitive content. When the user authorizes pushes, push each commit to the assigned branch and verify the remote accepted it before starting the next increment. Preserve existing history and resolve push failures without force pushing or destructive resets.

The team uses `main` as the stable branch, `backend` for the Flask API, `frontend` for UI development, and `integration` to bring the components together and test them.
