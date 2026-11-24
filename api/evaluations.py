from flask import Blueprint, jsonify, request

from database import MYSQL_INT_MAX, database_cursor

from .criteria import CRITERIA, load_criteria
from .errors import ApiError

bp = Blueprint("evaluations", __name__, url_prefix="/api")


def _validate_evaluation(payload):
    if not isinstance(payload, dict):
        raise ApiError("invalid_evaluation", "Send a JSON object with the software ID and four scores.", 400)

    software_id = payload.get("software_id")
    if type(software_id) is not int or not 1 <= software_id <= MYSQL_INT_MAX:
        raise ApiError("invalid_evaluation", "software_id must be a positive integer ID.", 400)

    for criterion in CRITERIA:
        score = payload.get(criterion)
        if type(score) is not int or not 1 <= score <= 10:
            raise ApiError("invalid_evaluation", f"{criterion} must be an integer from 1 to 10.", 400)

    return software_id


@bp.post("/evaluations")
def create_evaluation():
    payload = request.get_json(silent=True)
    software_id = _validate_evaluation(payload)

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
