# SoftReview Hub security

Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

## Credentials and data

- Configure the connection through environment variables. Use `.env.example` as a template with placeholder values and keep the local `.env` file out of Git.
- Keep private keys, dumps, and files containing personal data, including the original dataset, out of Git. Use fictitious test data. MySQL and the API handle only anonymous evaluator IDs.
- Inspect tracked paths as well as ignore rules before pushing. If a secret is found, identify only its file or variable, stop the affected push, and correct the exposure. If it reached the remote, notify the owner so they can rotate it.
- Keep secrets, queries, and stack traces out of HTTP responses. Keep credentials, course data, and assigned infrastructure identifiers out of logs, public documentation, and shared examples. Error messages should explain the problem and, when applicable, how to fix it.

## Queries and the shared server

- Parameterize SQL values. In `/api/tables/<name>`, resolve the requested name through an explicit mapping of the seven project tables (`Brand`, `ProductType`, `SoftwareSystem`, `Evaluator`, `EvaluationReport`, `ScoreCriterion`, and `EvaluationScore`). Use allowlists for any option that selects a SQL identifier or the ranking order.
- Validate in Flask that the four scores are integers between 1 and 10. Save the report and its scores in a single InnoDB transaction.
- Close cursors and connections after each operation, including failures. Return API errors using the agreed JSON format.
- Limit server operations to the assigned account, the assigned database, and the assigned directories. Use the minimum privileges available. Before running existing SQL, review `CREATE DATABASE`, `USE`, and `DROP` statements and confirm the target database.
- For remote testing, use only the authorized interfaces for Flask, Gunicorn, and MySQL. Access HTTP through the agreed SSH tunnel and keep debug mode disabled. Coordinate any public access or server configuration changes with the university.
- Use an isolated development database on Windows and bind Gunicorn to localhost on Linux. Inspect the existing schema in the assigned database before running any DDL and preserve existing tables and data.

## Linux verification

Check out the revision you intend to verify after cloning the repository, or transfer a Git archive from Windows when the server lacks GitHub access. `git archive` packages tracked files from the selected commit. Fill in the SSH login and host before transferring.

```powershell
$revision = (git rev-parse HEAD).Trim()
$archive = Join-Path ([IO.Path]::GetTempPath()) "softreview-$revision.tar.gz"
git archive --format=tar.gz --output=$archive $revision
if ($LASTEXITCODE -ne 0) { throw 'git archive failed' }
$sshTarget = 'YOUR_SSH_LOGIN@YOUR_UNIVERSITY_HOST'
scp $archive "${sshTarget}:softreview-$revision.tar.gz"
```

On Linux, extract the archive into an assigned directory. If the server can access GitHub, clone the repository and use `git checkout --detach "$revision"` with the same hash.

```bash
revision=YOUR_TESTED_COMMIT
release_dir="$HOME/softreview-$revision"
mkdir -p "$release_dir"
tar -xzf "$HOME/softreview-$revision.tar.gz" -C "$release_dir"
cd "$release_dir"
```

Run the following from the revision's root.

```bash
export DB_HOST=127.0.0.1 DB_PORT=3306 DB_NAME='YOUR_ASSIGNED_DB' DB_USER='YOUR_ASSIGNED_DB_USER' FLASK_DEBUG=0
mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p "$DB_NAME" -e 'SHOW TABLES'
# If all seven application tables are absent and setup is authorized:
# mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p "$DB_NAME" < sql/create_tables.sql
# If criteria are missing and seeding is authorized:
# mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p "$DB_NAME" < sql/seed_criteria.sql
read -rsp 'MySQL password: ' DB_PASSWORD
printf '\n'
export DB_PASSWORD
uv sync --locked --python 3.12
uv run --locked gunicorn --bind 127.0.0.1:8000 app:app
```

Replace the database and user placeholders with your assigned MySQL settings. Keep the real host, account, database name, and credentials in your local configuration or the team’s approved private notes. For a Unix socket, set `DB_UNIX_SOCKET` to its authorized path and use `mysql --protocol=SOCKET --socket="$DB_UNIX_SOCKET"` with the same user and database. If only some application tables exist, verify the existing definitions and coordinate the missing schema before applying DDL. Preserve existing tables and data. The fictitious fixture is for isolated development.

Run these checks from a second SSH terminal or adapt the base URL to the local port of the agreed SSH tunnel.

```bash
base=http://127.0.0.1:8000
for endpoint in /health /api/software /api/tables /api/tables/Brand /api/criteria \
    '/api/rankings?n=5&order=best' '/api/rankings?n=5&order=worst' \
    '/api/rankings?n=2&order=best&criterion=price&product_type_id=1'; do
  curl -fsS "$base$endpoint"
  printf '\n'
done

# Authorized test data only. Replace 1 with an approved software_id from /api/software.
# curl -si "$base/api/evaluations" -H 'Content-Type: application/json' \
#   --data '{"software_id":1,"friendliness":8,"price":7,"features":9,"accuracy":10}'
```

The read requests should return HTTP 200. The authorized POST should return HTTP 201. After stopping Gunicorn, clear the password from the shell with `unset DB_PASSWORD`.

## If a secret is exposed

Revoke or rotate the exposed credential or key immediately. Notify the team and, if university resources are affected, the server administrator or university IT support. If personal data is involved, also follow the university's reporting process. Identify where the secret was shared, remove it from those locations, and coordinate any Git history cleanup with the team. Revocation or rotation is required even after the secret is removed from a file.
