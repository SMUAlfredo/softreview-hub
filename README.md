# SoftReview Hub

Final project for Database (MCDA 5540, Fall 2026). SoftReview Hub lets users browse software data, submit evaluations, and compare systems.

The backend uses Python 3.12, Flask, MySQL Connector/Python, and Gunicorn on Linux. The frontend uses HTML, CSS, Bootstrap, and JavaScript.

## Main files

- `app.py` defines the Flask API routes and JSON responses.
- `pyproject.toml` declares the project and its dependencies. `uv.lock` pins the versions uv installs.
- `database.py` opens MySQL connections and handles cursor cleanup and write transactions.
- `.env.example` lists the MySQL environment variables. `.gitignore` excludes the virtual environment, credentials, and local data.
- `AGENTS.md` contains working instructions for Codex.
- `SECURITY.md` covers credentials, data, and use of the university server.
- `UPDATE.md` records changes, checks performed, and pending work.

## Local environment

Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

Install uv and run these commands from the root of the clone.

Set `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in the process environment for database routes. TCP defaults to `DB_HOST=127.0.0.1` and `DB_PORT=3306`. Set `DB_UNIX_SOCKET` to use a local Unix socket instead. Use `.env.example` as a reference when setting environment variables. `/health` works without database settings.

### Windows PowerShell

```powershell
uv sync --locked --python 3.12
uv run --locked flask --app app run --host 127.0.0.1 --port 5000
```

Send the health request from a second PowerShell terminal.

```powershell
curl.exe -i http://127.0.0.1:5000/health
```

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

## University Linux verification

Check out the exact tested revision after cloning the private repository, or transfer a Git archive from Windows when the server lacks GitHub access. `git archive` packages tracked files from the selected commit. Fill in the SSH login and host before transferring.

```powershell
$revision = (git rev-parse HEAD).Trim()
$archive = Join-Path ([IO.Path]::GetTempPath()) "softreview-$revision.tar.gz"
git archive --format=tar.gz --output=$archive $revision
if ($LASTEXITCODE -ne 0) { throw 'git archive failed' }
$sshTarget = 'YOUR_SSH_LOGIN@YOUR_UNIVERSITY_HOST'
scp $archive "${sshTarget}:softreview-$revision.tar.gz"
```

On Linux, extract the archive into an assigned directory. If the server can access GitHub, clone the private repository and use `git checkout --detach "$revision"` with the same hash.

```bash
revision=YOUR_TESTED_COMMIT
release_dir="$HOME/softreview-$revision"
mkdir -p "$release_dir"
tar -xzf "$HOME/softreview-$revision.tar.gz" -C "$release_dir"
cd "$release_dir"
```

Run the following from the revision's root.

```bash
export DB_HOST=127.0.0.1 DB_PORT=3306 DB_NAME=u07 DB_USER=u07 FLASK_DEBUG=0
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

Use the assigned MySQL connection. For a Unix socket, set `DB_UNIX_SOCKET` to its authorized path and use `mysql --protocol=SOCKET --socket="$DB_UNIX_SOCKET"` with the same user and database. If only some application tables exist, verify the existing definitions and coordinate the missing schema before applying DDL. Preserve existing tables and data. The fictitious fixture is for isolated development.

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

## Schema and data

| Table | Columns |
| --- | --- |
| `Brand` | `brand_id`, `brand_name` |
| `ProductType` | `product_type_id`, `type_name` |
| `SoftwareSystem` | `software_id`, `brand_id`, `product_type_id` |
| `Evaluator` | `evaluator_id` |
| `EvaluationReport` | `report_id`, `evaluator_id`, `software_id` |
| `ScoreCriterion` | `criterion_id`, `criterion_name` |
| `EvaluationScore` | `report_id`, `criterion_id`, `score_value` |

The design uses InnoDB and foreign keys. Brand, product type, and criterion names are unique, as is each system's `(brand_id, product_type_id)` pair. The primary key of `EvaluationScore` is `(report_id, criterion_id)`. Valid scores are integers from 1 to 10.

`project.json` contains one JSON document per line. Task 4 uses the 100 software documents with 4,738 evaluations and excludes the 100 profile documents. The planned import goes through MongoDB before MySQL. Keep original email addresses out of MySQL, the API, and Git. Backend tests use fictitious data.

The scripts for Tasks 3b and 4 are submitted separately. Local copies of `create_tables.sql`, `create_db.sh`, and `data2mongo2sql.sh` are in the course project folder outside the clone. The reviewed DDL leaves database selection to the client. The scripts generate database creation and selection statements from the supplied name. The reviewed copy of `data2mongo2sql.sh` ends after table creation.

Use `sql/create_tables.sql` to install the course schema in an empty, explicitly selected database. Run `sql/seed_criteria.sql` to add missing criteria while retaining existing IDs. Use `sql/test_data.sql` in a fresh isolated development database for fictitious records.

For development, use a separate local database such as `softreview_dev` with a development account and select it with `DB_NAME`. On the server, set `DB_NAME=u07` and use the assigned account. Before running SQL or scripts, confirm the target database and review any `CREATE DATABASE`, `USE`, and `DROP` statements.

## Workflow and deliverables

The team develops locally in VS Code, integrates changes through the private GitHub repository, and deploys to the university's Linux server. `main` is the stable branch, `backend` holds Flask API changes, `frontend` is for UI development, and `integration` is for integrating and testing components.

Use Gunicorn on localhost with debug disabled and access HTTP through the agreed SSH tunnel. `UPDATE.md` records the reported infrastructure checks and the backend tests run on Windows.

Task 5 demonstrates table browsing, transactional evaluation submission, and ranking by criterion. Task 6 includes a roughly 15-minute presentation with all three team members and a 2–4-page PDF report about the application structure and how its files connect. The work is divided across three roles covering the backend and README, the frontend, and integration, testing, and the report.
