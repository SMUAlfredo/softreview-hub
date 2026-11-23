# SoftReview Hub

Final project for Database (MCDA 5540, Fall 2026). SoftReview Hub lets users browse software data, submit evaluations, and compare systems.

The backend uses Python 3.12 and Flask. The planned stack includes MySQL Connector/Python for database access and Gunicorn for serving the application on Linux. The frontend uses HTML, CSS, Bootstrap, and JavaScript.

## Main files

- `pyproject.toml` declares the project and its dependencies. `uv.lock` pins the versions uv installs.
- `.env.example` lists the planned MySQL environment variables. `.gitignore` excludes the virtual environment, credentials, and local data.
- `AGENTS.md` contains working instructions for Codex.
- `SECURITY.md` covers credentials, data, and use of the university server.
- `UPDATE.md` records changes, checks performed, and pending work.

## Local environment

Always use uv for Python. Add dependencies with `uv add`, reproduce the environment with `uv sync --locked`, and run Flask, scripts, and tests with `uv run`. Track `pyproject.toml` and `uv.lock` in Git. Avoid `pip`, `python -m pip`, and `uv pip` for dependency management.

Install uv and run these commands from the root of the clone.

For the future MySQL connection, copy `.env.example` to `.env` and set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` for your environment. Git ignores the local file. Flask currently starts without these variables.

### Windows PowerShell

```powershell
uv sync --locked --python 3.12
uv run --locked flask --app app run --host 127.0.0.1 --port 5000
```

Send the health request from a second PowerShell terminal.

```powershell
curl.exe -i http://127.0.0.1:5000/health
```

### Linux

```bash
uv sync --locked --python 3.12
uv run --locked flask --app app run --host 127.0.0.1 --port 5000
```

Send the health request from a second terminal.

```bash
curl -i http://127.0.0.1:5000/health
```

## Frontend API contract

| Method and path | Expected result | Status |
| --- | --- | --- |
| `GET /health` | HTTP 200 with JSON, without a MySQL connection | Planned for this stage |
| `GET /api/tables` | List of the seven tables | Pending |
| `GET /api/tables/<name>` | Contents of an allowed table | Pending |
| `GET /api/software` | Software available for evaluation | Pending |
| `GET /api/criteria` | Evaluation criteria | Pending |
| `POST /api/evaluations` | One report and its four scores in a single transaction | Pending |
| `GET /api/rankings?n=5&order=best` | The five highest-ranked systems | Pending |
| `GET /api/rankings?n=5&order=worst` | The five lowest-ranked systems | Pending |

Successful responses use `{"success":true,"data":{...}}`. Errors use `{"success":false,"error":{"code":"...","message":"..."}}`.

Use the agreed request body to submit an evaluation.

```json
{"software_id":1,"friendliness":8,"price":7,"features":9,"accuracy":10}
```

The backend validates that the software exists and that the four scores are integers from 1 to 10. The server will assign the anonymous evaluator ID. Confirm how IDs will be assigned before implementing the write operation. If any insert fails, roll back the entire transaction.

Rankings use the average score for the selected criterion. The frontend and backend teams still need to agree on the names and default values of the additional parameters for selecting a criterion and filtering by product type.

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

For development, use a separate local database such as `softreview_dev` with a development account. Once MySQL support is added to the backend, select that database with `DB_NAME` in the local environment. On the server, set `DB_NAME=u07` and use the assigned account. Before running SQL or scripts, confirm the target database and review any `CREATE DATABASE`, `USE`, and `DROP` statements.

## Workflow and deliverables

The team develops locally in VS Code, integrates changes through the private GitHub repository, and deploys to the university's Linux server. `main` is the stable branch, `frontend` is for UI development, and `integration` is for integrating and testing components. Commits from this stage stay local until a push is requested.

On Linux, the plan is to serve the application with Gunicorn, disable debug mode, and access HTTP through the agreed SSH tunnel. `UPDATE.md` records the infrastructure checks reported by the team.

Task 5 demonstrates table browsing, transactional evaluation submission, and ranking by criterion. Task 6 includes a roughly 15-minute presentation with all three team members and a 2–4-page PDF report about the application structure and how its files connect. The work is divided across three roles covering the backend and README, the frontend, and integration, testing, and the report.
