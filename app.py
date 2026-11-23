from flask import Flask, jsonify, request
from mysql.connector import Error as MySQLError
from werkzeug.exceptions import HTTPException

from database import DatabaseUnavailable, database_cursor

app = Flask(__name__)

TABLE_QUERIES = {
    "Brand": "SELECT brand_id, brand_name FROM Brand ORDER BY brand_id",
    "ProductType": "SELECT product_type_id, type_name FROM ProductType ORDER BY product_type_id",
    "SoftwareSystem": "SELECT software_id, brand_id, product_type_id FROM SoftwareSystem ORDER BY software_id",
    "Evaluator": "SELECT evaluator_id FROM Evaluator ORDER BY evaluator_id",
    "EvaluationReport": "SELECT report_id, evaluator_id, software_id FROM EvaluationReport ORDER BY report_id",
    "ScoreCriterion": "SELECT criterion_id, criterion_name FROM ScoreCriterion ORDER BY criterion_id",
    "EvaluationScore": "SELECT report_id, criterion_id, score_value FROM EvaluationScore ORDER BY report_id, criterion_id",
}
CRITERIA = ("friendliness", "price", "features", "accuracy")


class ApiError(Exception):
    def __init__(self, code, message, status):
        super().__init__(message)
        self.code = code
        self.status = status


@app.get("/health")
def health():
    return jsonify(success=True, data={"status": "ok"})


def error_response(code, message, status):
    return jsonify(success=False, error={"code": code, "message": message}), status


@app.errorhandler(ApiError)
def api_error(error):
    return error_response(error.code, str(error), error.status)


@app.errorhandler(DatabaseUnavailable)
def database_unavailable(_error):
    return error_response(
        "database_unavailable", "Database connection unavailable. Check the server configuration.", 503
    )


@app.errorhandler(MySQLError)
def database_error(_error):
    app.logger.error("A database operation failed.")
    return error_response("database_error", "The database operation could not be completed.", 500)


@app.errorhandler(HTTPException)
def http_error(error):
    response = error.get_response()
    response.set_data(app.json.dumps({
        "success": False,
        "error": {"code": error.name.lower().replace(" ", "_"), "message": error.name},
    }))
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def unexpected_error(error):
    app.logger.error("Unexpected application error (%s).", type(error).__name__)
    return error_response("internal_error", "The request could not be completed.", 500)


@app.get("/api/tables")
def tables():
    return jsonify(success=True, data=list(TABLE_QUERIES))


@app.get("/api/tables/<name>")
def table(name):
    query = TABLE_QUERIES.get(name)
    if query is None:
        raise ApiError("unknown_table", "Select a table listed by /api/tables.", 404)

    with database_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return jsonify(success=True, data=rows)


def load_criteria(cursor):
    cursor.execute(
        """
        SELECT criterion_id, LOWER(criterion_name) AS criterion_name
        FROM ScoreCriterion
        WHERE LOWER(criterion_name) IN (%s, %s, %s, %s)
        """,
        CRITERIA,
    )
    rows = cursor.fetchall()
    by_name = {row["criterion_name"]: row for row in rows}
    if len(rows) != len(CRITERIA) or any(name not in by_name for name in CRITERIA):
        raise ApiError(
            "criteria_unavailable", "The four required evaluation criteria must be configured once each.", 503
        )
    return by_name


@app.get("/api/criteria")
def criteria():
    with database_cursor() as cursor:
        by_name = load_criteria(cursor)
    return jsonify(success=True, data=[by_name[name] for name in CRITERIA])


@app.get("/api/software")
def software():
    with database_cursor() as cursor:
        cursor.execute(
            """
            SELECT s.software_id, s.brand_id, b.brand_name, s.product_type_id, p.type_name
            FROM SoftwareSystem AS s
            JOIN Brand AS b ON b.brand_id = s.brand_id
            JOIN ProductType AS p ON p.product_type_id = s.product_type_id
            ORDER BY s.software_id
            """
        )
        rows = cursor.fetchall()
    return jsonify(success=True, data=rows)


def validate_evaluation(payload):
    if not isinstance(payload, dict):
        raise ApiError("invalid_evaluation", "Send a JSON object with the software ID and four scores.", 400)

    software_id = payload.get("software_id")
    if type(software_id) is not int or not 1 <= software_id <= 2_147_483_647:
        raise ApiError("invalid_evaluation", "software_id must be a positive integer ID.", 400)

    for criterion in CRITERIA:
        score = payload.get(criterion)
        if type(score) is not int or not 1 <= score <= 10:
            raise ApiError("invalid_evaluation", f"{criterion} must be an integer from 1 to 10.", 400)


@app.post("/api/evaluations")
def create_evaluation():
    payload = request.get_json(silent=True)
    validate_evaluation(payload)
    software_id = payload["software_id"]

    with database_cursor(write=True) as cursor:
        cursor.execute("SELECT software_id FROM SoftwareSystem WHERE software_id = %s", (software_id,))
        if cursor.fetchone() is None:
            raise ApiError("unknown_software", "Select a software system listed by /api/software.", 404)

        by_name = load_criteria(cursor)
        cursor.execute("INSERT INTO Evaluator () VALUES ()")
        evaluator_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO EvaluationReport (evaluator_id, software_id) VALUES (%s, %s)",
            (evaluator_id, software_id),
        )
        report_id = cursor.lastrowid
        cursor.executemany(
            """
            INSERT INTO EvaluationScore (report_id, criterion_id, score_value)
            VALUES (%s, %s, %s)
            """,
            [(report_id, by_name[name]["criterion_id"], payload[name]) for name in CRITERIA],
        )

    return jsonify(success=True, data={"report_id": report_id, "software_id": software_id}), 201
