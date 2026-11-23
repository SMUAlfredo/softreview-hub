# SoftReview Hub

SoftReview Hub is a Flask and MySQL API for browsing software data, submitting evaluations, and ranking systems by criterion. The backend uses Python 3.12 and runs locally with Flask or on Linux with Gunicorn.

## Local development

Install [uv](https://docs.astral.sh/uv/) and use it for Python dependencies and commands. A local MySQL 8 instance is required for database routes. Run the commands below from the root of the clone.

Set `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in the process environment for database routes. TCP defaults to `DB_HOST=127.0.0.1` and `DB_PORT=3306`. Set `DB_UNIX_SOCKET` to use a local Unix socket instead. Use `.env.example` as a reference when setting environment variables.

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

Set the backend account in PowerShell before starting Flask again. Adjust the port for the isolated instance. If MySQL CLI tools are outside `PATH`, use their full paths.

```powershell
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '3306'
$env:DB_NAME = 'softreview_test'
$env:DB_USER = 'YOUR_LOCAL_TEST_USER'
$env:DB_PASSWORD = [Net.NetworkCredential]::new('', (Read-Host 'MySQL password' -AsSecureString)).Password
$env:FLASK_DEBUG = '0'
uv run --locked flask --app app run --host 127.0.0.1 --port 5000
```

### Tests

`uv run --locked python -m unittest discover -s tests -v` runs isolated tests and skips MySQL integration tests by default. With the fictitious fixture loaded, run the same command with `SOFTREVIEW_TEST_MYSQL=1` in the environment. In PowerShell, use `$env:SOFTREVIEW_TEST_MYSQL = '1'`. The integration suite requires the isolated `softreview_test` database. Use a local test account with SELECT, INSERT, DELETE, and TRIGGER privileges in that database. Use an isolated instance that permits the temporary rollback test trigger, for example with binary logging disabled.

## Project files

- `app.py` defines the Flask routes and JSON responses.
- `database.py` manages MySQL connections and transactions.
- `sql/` contains the schema, criteria seed, and fictitious development data.
- `tests/` contains the isolated and MySQL integration tests.
- `pyproject.toml` and `uv.lock` define the reproducible Python environment.

The team shares integration instructions directly through an approved private channel. See [SECURITY.md](SECURITY.md) for handling credentials and service access, [UPDATE.md](UPDATE.md) for test results and project status, and [AGENTS.md](AGENTS.md) for development workflow.
