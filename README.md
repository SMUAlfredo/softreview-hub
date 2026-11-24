# SoftReview Hub

SoftReview Hub is a Flask and MySQL API for browsing software data, submitting evaluations, and ranking systems by criterion. The backend uses Python 3.12 and runs locally with Flask.

## Local development

Install [uv](https://docs.astral.sh/uv/) and have MySQL 8 running on your machine. Run the setup commands from the root of the clone. If the MySQL client is outside `PATH`, use its full path.

The API connects to MySQL over TCP at `127.0.0.1`. Set `DB_NAME`, `DB_USER`, and `DB_PASSWORD` for database routes. The default port is `3306` and can be changed with `DB_PORT`.

### Prepare the database once

Use the account that can create a database on your local MySQL. Replace `3306` if your instance uses another port. Run the second command after the first succeeds.

```sh
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u YOUR_LOCAL_SETUP_USER -p -e 'CREATE DATABASE softreview_dev CHARACTER SET utf8mb4'
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u YOUR_LOCAL_SETUP_USER -p -e 'SOURCE sql/setup_local.sql' softreview_dev
```

The setup creates the tables and loads the four evaluation criteria. If you need a separate app account, connect to your local MySQL with your setup account and run these statements with a local password of your choice.

```sql
CREATE USER 'softreview_dev_user'@'localhost' IDENTIFIED BY 'YOUR_LOCAL_PASSWORD';
GRANT SELECT, INSERT ON softreview_dev.* TO 'softreview_dev_user'@'localhost';
```

### Start the API

Copy `.env.example` to `.env` and set the user, password, and port for your local MySQL. Git ignores `.env`. Install the locked Python dependencies once, then start Flask.

```sh
uv sync --locked --python 3.12
uv run --locked --env-file .env flask --app app run --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000/api/criteria` to check the database connection. The catalog starts empty after this setup.

### Import the course dataset

Each teammate needs their own copy of `project.json`. Keep it outside the clone. After setting up a fresh `softreview_dev` database and filling in `.env`, run this from the clone root. Replace the example path with the location of your file.

```sh
uv run --locked --env-file .env python -m scripts.import_course_data ../project.json
```

The importer uses the local database in `.env`, skips profile records, and stores numeric evaluator IDs. It commits the import as a single transaction and stops if the target already has catalog or evaluator data. Open `http://127.0.0.1:5000/api/software` after starting Flask to check the catalog.

### Tests

`uv run --locked python -m unittest discover -s tests -v` runs isolated tests and skips MySQL integration tests by default. For integration tests, use the same schema setup commands with a fresh `softreview_test` database, then load `sql/test_data.sql` into it. Copy `.env.example` to `.env.test` and set `DB_NAME=softreview_test` and the local test account. Set `$env:SOFTREVIEW_TEST_MYSQL = '1'` in PowerShell or `export SOFTREVIEW_TEST_MYSQL=1` in a POSIX shell, then run `uv run --locked --env-file .env.test python -m unittest discover -s tests -v`. The test account needs SELECT, INSERT, DELETE, and TRIGGER privileges. Use an isolated instance that permits the temporary rollback test trigger, for example with binary logging disabled.

## Project files

- `app.py` starts Flask, registers the route groups, and defines the health check.
- `api/` groups routes by feature in `catalog.py`, `criteria.py`, `evaluations.py`, and `rankings.py`. `errors.py` handles JSON errors for the whole app.
- `database.py` manages MySQL connections and transactions.
- `scripts/` contains the command-line importer for the course dataset.
- `sql/` contains the schema, criteria seed, and fictitious development data.
- `tests/` contains the isolated and MySQL integration tests.
- `pyproject.toml` and `uv.lock` define the reproducible Python environment.

The team shares integration instructions directly through an approved private channel. See [SECURITY.md](SECURITY.md) for handling credentials and service access, [UPDATE.md](UPDATE.md) for test results and project status, and [AGENTS.md](AGENTS.md) for development workflow.
