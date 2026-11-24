import json
from dataclasses import dataclass, field

from api.criteria import CRITERIA

PROFILE_FIELDS = {"first_name", "last_name", "email", "country"}
SOFTWARE_FIELDS = {"brand", "product_type", "scores"}


class CourseDataError(ValueError):
    """An import error whose message contains no source records."""


@dataclass
class CourseData:
    brands: dict[str, int] = field(default_factory=dict)
    product_types: dict[str, int] = field(default_factory=dict)
    software: dict[tuple[int, int], int] = field(default_factory=dict)
    evaluator_count: int = 0
    reports: list[tuple[int, int, int]] = field(default_factory=list)
    scores: list[tuple[int, str, int]] = field(default_factory=list)


def read_course_data(source):
    data = CourseData()
    evaluator_ids = {}

    with source.open(encoding="utf-8-sig") as lines:
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except (ValueError, RecursionError):
                raise CourseDataError(f"Invalid JSON on line {line_number}.") from None
            if not isinstance(record, dict):
                raise CourseDataError(f"Expected a JSON object on line {line_number}.")
            if PROFILE_FIELDS <= record.keys() and SOFTWARE_FIELDS.isdisjoint(record):
                continue
            _add_software(data, evaluator_ids, record, line_number)

    if not data.software:
        raise CourseDataError("The source file contains no software records.")
    data.evaluator_count = len(evaluator_ids)
    return data


def _add_software(data, evaluator_ids, record, line_number):
    brand = record.get("brand")
    product_type = record.get("product_type")
    evaluations = record.get("scores")
    if (
        not isinstance(brand, str) or not brand.strip() or len(brand) > 150
        or not isinstance(product_type, str) or not product_type.strip() or len(product_type) > 100
        or not isinstance(evaluations, list)
    ):
        raise CourseDataError(f"Invalid software record on line {line_number}.")

    brand_id = data.brands.setdefault(brand, len(data.brands) + 1)
    type_id = data.product_types.setdefault(product_type, len(data.product_types) + 1)
    software_id = data.software.setdefault((brand_id, type_id), len(data.software) + 1)

    for index, evaluation in enumerate(evaluations, 1):
        who, values = _evaluation_values(evaluation, line_number, index)
        evaluator_id = evaluator_ids.setdefault(who, len(evaluator_ids) + 1)
        report_id = len(data.reports) + 1
        data.reports.append((report_id, evaluator_id, software_id))
        data.scores.extend(
            (report_id, criterion, value) for criterion, value in zip(CRITERIA, values, strict=True)
        )


def _evaluation_values(evaluation, line_number, index):
    if isinstance(evaluation, dict):
        who = evaluation.get("who")
        values = [evaluation.get(criterion) for criterion in CRITERIA]
        if isinstance(who, str) and who.strip() and all(type(value) is int and 1 <= value <= 10 for value in values):
            return who, values
    raise CourseDataError(f"Invalid evaluation {index} on line {line_number}.")
