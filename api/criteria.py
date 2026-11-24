from flask import Blueprint, jsonify

from database import database_cursor

from .errors import ApiError

bp = Blueprint("criteria", __name__, url_prefix="/api")
CRITERIA = ("friendliness", "price", "features", "accuracy")


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
    if len(rows) != len(CRITERIA) or by_name.keys() != set(CRITERIA):
        raise ApiError(
            "criteria_unavailable", "The four required evaluation criteria must be configured once each.", 503
        )
    return by_name


@bp.get("/criteria")
def criteria():
    with database_cursor() as cursor:
        by_name = load_criteria(cursor)
    return jsonify(success=True, data=[by_name[name] for name in CRITERIA])
