from flask import Flask, jsonify
from mysql.connector import Error as MySQLError
from werkzeug.exceptions import HTTPException

from database import DatabaseUnavailable, database_cursor

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(success=True, data={"status": "ok"})


def error_response(code, message, status):
    return jsonify(success=False, error={"code": code, "message": message}), status


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
