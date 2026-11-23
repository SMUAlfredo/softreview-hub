# SoftReview Hub

SoftReview Hub is a Flask and MySQL API for browsing software data, submitting evaluations, and ranking systems by criterion. The backend uses Python 3.12 and runs locally with Flask or on Linux with Gunicorn.

## Local development

Install [uv](https://docs.astral.sh/uv/) and use it for Python dependencies and commands. A local MySQL 8 instance is required for database routes. Run the commands below from the root of the clone.

Set `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in the process environment for database routes. TCP defaults to `DB_HOST=127.0.0.1` and `DB_PORT=3306`. Set `DB_UNIX_SOCKET` to use a local Unix socket instead. Use `.env.example` as a reference when setting environment variables. `/health` works without database settings.

### Start the API

```powershell
uv sync --locked --python 3.12
uv run --locked flask --app app run --host 127.0.0.1 --port 5000
```

Send the health request from a second PowerShell terminal.

```powershell
curl.exe -i http://127.0.0.1:5000/health
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

## Frontend API contract

| Method and path | Expected result | Status |
| --- | --- | --- |
| `GET /health` | HTTP 200 with `{"success":true,"data":{"status":"ok"}}`, without a MySQL connection | Implemented |
| `GET /api/tables` | Array of the seven canonical table names | Implemented |
| `GET /api/tables/<name>` | Array of rows from an allowed table | Implemented |
| `GET /api/software` | Software sorted by ID, with brand and product type details | Implemented |
| `GET /api/criteria` | Array of criterion IDs and canonical names | Implemented |
| `POST /api/evaluations` | HTTP 201 for one report and its four scores in a single transaction | Implemented |
| `GET /api/rankings?n=5&order=best` | Up to five highest-ranked systems | Implemented |
| `GET /api/rankings?n=5&order=worst` | Up to five lowest-ranked systems | Implemented |

Successful responses use `{"success":true,"data":...}`. Errors use `{"success":false,"error":{"code":"...","message":"..."}}`.

Use the exact table name returned by `GET /api/tables`, such as `GET /api/tables/Brand`. An unknown name returns 404 with code `unknown_table`. The criteria endpoint returns `criterion_id` and `criterion_name` for `friendliness`, `price`, `features`, and `accuracy` in that order.

`GET /api/software` returns an array in `data`. A row from the development fixture looks like this.

```json
{"software_id":1,"brand_id":1,"brand_name":"Atlas","product_type_id":1,"type_name":"Editor"}
```

Use the agreed request body to submit an evaluation.

```json
{"software_id":1,"friendliness":8,"price":7,"features":9,"accuracy":10}
```

The backend requires an existing software ID and four integer scores from 1 to 10. It creates one anonymous evaluator per submission and rolls back the evaluator, report, and scores together if a write fails. A successful submission returns HTTP 201 with `{"success":true,"data":{"report_id":1,"software_id":1}}`. Invalid input returns 400 and an unknown software ID returns 404.

Rankings use the average score for the selected criterion. The query parameters are `n` (default `5`), `order` (`best` by default, or `worst`), `criterion` (`friendliness` by default, or `price`, `features`, or `accuracy`), and optional `product_type_id` (all types by default). Both numeric parameters accept positive MySQL INT values. Invalid parameters return 400. An unknown product type returns an empty array.

Systems need at least one score for the chosen criterion. Ties sort by ascending `software_id` in both directions. Rows include the software catalog fields plus numeric `average_score` and `evaluation_count`. For example, `GET /api/rankings?n=2&order=best&criterion=price&product_type_id=1` returns Cedar (9.0) followed by Atlas (5.0) with the development fixture.

## Project files

- `app.py` defines the Flask routes and JSON responses.
- `database.py` manages MySQL connections and transactions.
- `sql/` contains the schema, criteria seed, and fictitious development data.
- `tests/` contains the isolated and MySQL integration tests.
- `pyproject.toml` and `uv.lock` define the reproducible Python environment.

See [SECURITY.md](SECURITY.md) for credential handling and Linux verification, [UPDATE.md](UPDATE.md) for test results and project status, and [AGENTS.md](AGENTS.md) for development workflow.
