import argparse
from pathlib import Path

from mysql.connector import Error as MySQLError

from api.criteria import load_criteria
from api.errors import ApiError
from database import DatabaseUnavailable, database_cursor

from .course_data import CourseDataError, read_course_data


def _insert_course_data(data):
    with database_cursor(write=True) as cursor:
        # MySQL releases the lock when the connection closes, after commit or rollback.
        cursor.execute(
            "SELECT GET_LOCK(SHA2(CONCAT('softreview-import:', DATABASE()), 256), 5) AS acquired"
        )
        if cursor.fetchone()["acquired"] != 1:
            raise CourseDataError("Another import is running. Try again after it finishes.")

        cursor.execute(
            """
            SELECT EXISTS (SELECT 1 FROM Brand)
                OR EXISTS (SELECT 1 FROM ProductType)
                OR EXISTS (SELECT 1 FROM Evaluator) AS has_data
            """
        )
        if cursor.fetchone()["has_data"]:
            raise CourseDataError("The target database already has data. Use a fresh local database.")

        criteria = load_criteria(cursor)
        cursor.executemany(
            "INSERT INTO Brand (brand_id, brand_name) VALUES (%s, %s)",
            [(identifier, name) for name, identifier in data.brands.items()],
        )
        cursor.executemany(
            "INSERT INTO ProductType (product_type_id, type_name) VALUES (%s, %s)",
            [(identifier, name) for name, identifier in data.product_types.items()],
        )
        cursor.executemany(
            "INSERT INTO SoftwareSystem (software_id, brand_id, product_type_id) VALUES (%s, %s, %s)",
            [(identifier, brand_id, type_id) for (brand_id, type_id), identifier in data.software.items()],
        )
        if data.reports:
            cursor.executemany(
                "INSERT INTO Evaluator (evaluator_id) VALUES (%s)",
                [(identifier,) for identifier in range(1, data.evaluator_count + 1)],
            )
            cursor.executemany(
                "INSERT INTO EvaluationReport (report_id, evaluator_id, software_id) VALUES (%s, %s, %s)",
                data.reports,
            )
            cursor.executemany(
                "INSERT INTO EvaluationScore (report_id, criterion_id, score_value) VALUES (%s, %s, %s)",
                [(report_id, criteria[name]["criterion_id"], value) for report_id, name, value in data.scores],
            )


def main():
    parser = argparse.ArgumentParser(description="Load course data into a fresh local MySQL database.")
    parser.add_argument("source", type=Path, help="Path to the course JSON Lines file.")
    arguments = parser.parse_args()

    try:
        data = read_course_data(arguments.source)
        _insert_course_data(data)
    except CourseDataError as error:
        parser.exit(1, f"Import failed. {error}\n")
    except (OSError, UnicodeError):
        parser.exit(1, "Import failed. Check that the source file is readable UTF-8.\n")
    except DatabaseUnavailable:
        parser.exit(1, "Import failed. Check the local MySQL service and the settings in .env.\n")
    except ApiError:
        parser.exit(1, "Import failed. Load the four evaluation criteria before importing.\n")
    except MySQLError:
        parser.exit(1, "Import failed. Check the local schema and account permissions.\n")

    print(
        f"Imported {len(data.software)} software systems, {len(data.reports)} evaluations, "
        f"and {len(data.scores)} scores."
    )


if __name__ == "__main__":
    main()
