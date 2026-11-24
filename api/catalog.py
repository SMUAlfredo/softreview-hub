from flask import Blueprint, jsonify

from database import database_cursor

from .errors import ApiError

bp = Blueprint("catalog", __name__, url_prefix="/api")

TABLE_QUERIES = {
    "Brand": "SELECT brand_id, brand_name FROM Brand ORDER BY brand_id",
    "ProductType": "SELECT product_type_id, type_name FROM ProductType ORDER BY product_type_id",
    "SoftwareSystem": (
        "SELECT software_id, brand_id, product_type_id FROM SoftwareSystem ORDER BY software_id"
    ),
    "Evaluator": "SELECT evaluator_id FROM Evaluator ORDER BY evaluator_id",
    "EvaluationReport": (
        "SELECT report_id, evaluator_id, software_id FROM EvaluationReport ORDER BY report_id"
    ),
    "ScoreCriterion": "SELECT criterion_id, criterion_name FROM ScoreCriterion ORDER BY criterion_id",
    "EvaluationScore": (
        "SELECT report_id, criterion_id, score_value FROM EvaluationScore ORDER BY report_id, criterion_id"
    ),
}


@bp.get("/tables")
def tables():
    return jsonify(success=True, data=list(TABLE_QUERIES))


@bp.get("/tables/<name>")
def table(name):
    query = TABLE_QUERIES.get(name)
    if query is None:
        raise ApiError("unknown_table", "Select a table listed by /api/tables.", 404)

    with database_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return jsonify(success=True, data=rows)


@bp.get("/software")
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
