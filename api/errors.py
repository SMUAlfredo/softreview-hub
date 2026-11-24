from flask import current_app, jsonify
from mysql.connector import Error as MySQLError
from werkzeug.exceptions import HTTPException

from database import DatabaseUnavailable


class ApiError(Exception):
    def __init__(self, code, message, status):
        super().__init__(message)
        self.code = code
        self.status = status


def error_response(code, message, status):
    return jsonify(success=False, error={"code": code, "message": message}), status


def api_error(error):
    return error_response(error.code, str(error), error.status)


def database_unavailable(_error):
    return error_response(
        "database_unavailable", "Database connection unavailable. Check the server configuration.", 503
    )


def database_error(_error):
    current_app.logger.error("A database operation failed.")
    return error_response("database_error", "The database operation could not be completed.", 500)


def http_error(error):
    response = error.get_response()
    response.set_data(current_app.json.dumps({
        "success": False,
        "error": {"code": error.name.lower().replace(" ", "_"), "message": error.name},
    }))
    response.content_type = "application/json"
    return response


def unexpected_error(error):
    current_app.logger.error("Unexpected application error (%s).", type(error).__name__)
    return error_response("internal_error", "The request could not be completed.", 500)


def register_error_handlers(app):
    app.register_error_handler(ApiError, api_error)
    app.register_error_handler(DatabaseUnavailable, database_unavailable)
    app.register_error_handler(MySQLError, database_error)
    app.register_error_handler(HTTPException, http_error)
    app.register_error_handler(Exception, unexpected_error)
