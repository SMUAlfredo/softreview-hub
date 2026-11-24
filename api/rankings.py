from flask import Blueprint, jsonify, request

from database import MYSQL_INT_MAX, database_cursor

from .criteria import CRITERIA, load_criteria
from .errors import ApiError

bp = Blueprint("rankings", __name__, url_prefix="/api")
RANKING_DIRECTIONS = {"best": "DESC", "worst": "ASC"}


def _ranking_integer(name, value):
    if len(value) <= 10 and value.isascii() and value.isdecimal():
        number = int(value)
        if 1 <= number <= MYSQL_INT_MAX:
            return number
    raise ApiError("invalid_ranking", f"{name} must be an integer from 1 to {MYSQL_INT_MAX}.", 400)


@bp.get("/rankings")
def rankings():
    limit = _ranking_integer("n", request.args.get("n", "5"))
    direction = RANKING_DIRECTIONS.get(request.args.get("order", "best"))
    if direction is None:
        raise ApiError("invalid_ranking", "order must be best or worst.", 400)

    criterion = request.args.get("criterion", "friendliness")
    if criterion not in CRITERIA:
        raise ApiError("invalid_ranking", "criterion must be friendliness, price, features, or accuracy.", 400)

    product_type = request.args.get("product_type_id")
    product_type_filter = ""
    filter_values = ()
    if product_type is not None:
        product_type_filter = "AND s.product_type_id = %s"
        filter_values = (_ranking_integer("product_type_id", product_type),)

    with database_cursor() as cursor:
        criterion_id = load_criteria(cursor)[criterion]["criterion_id"]
        cursor.execute(
            f"""
            SELECT s.software_id, s.brand_id, b.brand_name, s.product_type_id, p.type_name,
                   AVG(CAST(es.score_value AS DECIMAL(14, 8))) AS average_score,
                   COUNT(*) AS evaluation_count
            FROM EvaluationScore AS es
            JOIN EvaluationReport AS er ON er.report_id = es.report_id
            JOIN SoftwareSystem AS s ON s.software_id = er.software_id
            JOIN Brand AS b ON b.brand_id = s.brand_id
            JOIN ProductType AS p ON p.product_type_id = s.product_type_id
            WHERE es.criterion_id = %s {product_type_filter}
            GROUP BY s.software_id, s.brand_id, b.brand_name, s.product_type_id, p.type_name
            ORDER BY average_score {direction}, s.software_id ASC
            LIMIT %s
            """,
            (criterion_id, *filter_values, limit),
        )
        rows = cursor.fetchall()

    for row in rows:
        row["average_score"] = float(row["average_score"])
    return jsonify(success=True, data=rows)
