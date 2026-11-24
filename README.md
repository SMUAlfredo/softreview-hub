# SoftReview Hub

SoftReview Hub is a Flask and MySQL API for browsing software data, submitting evaluations, and ranking systems by criterion. The backend uses Python 3.12 and runs locally with Flask.

## Local development

Install [uv](https://docs.astral.sh/uv/) and use it for Python dependencies and commands. A local MySQL 8 instance is required for database routes. Run the commands below from the root of the clone.

The API connects to MySQL over TCP at `127.0.0.1`. Set `DB_NAME`, `DB_USER`, and `DB_PASSWORD` for database routes. The default port is `3306` and can be changed with `DB_PORT`.

### Start the API

```powershell
uv sync --locked --python 3.12
uv run --locked flask --app app run --host 127.0.0.1 --port 5000
```

### Set up local MySQL

To test the database flows, create a fresh `softreview_test` database on an isolated local MySQL 8 instance. From the clone root, use the local schema setup account and port.

```powershell
$setupUser = 'YOUR_LOCAL_SCHEMA_SETUP_USER'
$mysqlPort = 3306
mysql.exe --protocol=TCP -h 127.0.0.1 -P $mysqlPort -u $setupUser -p -e 'CREATE DATABASE softreview_test CHARACTER SET utf8mb4'
mysql.exe --protocol=TCP -h 127.0.0.1 -P $mysqlPort -u $setupUser -p softreview_test
```

In the MySQL prompt, load the scripts in this order.

```sql
SOURCE sql/create_tables.sql;
SOURCE sql/seed_criteria.sql;
SOURCE sql/test_data.sql;
exit
```

Copy `.env.example` to `.env` once. Edit `.env` with the local backend account and the port of your isolated instance. If MySQL CLI tools are outside `PATH`, use their full paths. Start the API with the local configuration.

```powershell
uv run --locked --env-file .env flask --app app run --host 127.0.0.1 --port 5000
```

### Tests

`uv run --locked python -m unittest discover -s tests -v` runs isolated tests and skips MySQL integration tests by default. With the fictitious fixture loaded, set `$env:SOFTREVIEW_TEST_MYSQL = '1'` in PowerShell and run `uv run --locked --env-file .env python -m unittest discover -s tests -v`. The integration suite requires the isolated `softreview_test` database. Use a local test account with SELECT, INSERT, DELETE, and TRIGGER privileges in that database. Use an isolated instance that permits the temporary rollback test trigger, for example with binary logging disabled.

## Project files

- `app.py` defines the Flask routes and JSON responses.
- `database.py` manages MySQL connections and transactions.
- `sql/` contains the schema, criteria seed, and fictitious development data.
- `tests/` contains the isolated and MySQL integration tests.
- `pyproject.toml` and `uv.lock` define the reproducible Python environment.

The team shares integration instructions directly through an approved private channel. See [SECURITY.md](SECURITY.md) for handling credentials and service access, [UPDATE.md](UPDATE.md) for test results and project status, and [AGENTS.md](AGENTS.md) for development workflow.
