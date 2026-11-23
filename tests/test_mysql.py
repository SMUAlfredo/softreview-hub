import os
import unittest

from app import app
from database import database_cursor

EVALUATION = {"software_id": 1, "friendliness": 8, "price": 7, "features": 9, "accuracy": 10}


def evaluation_counts():
    with database_cursor() as cursor:
        cursor.execute(
            """
            SELECT (SELECT COUNT(*) FROM Evaluator) AS evaluators,
                   (SELECT COUNT(*) FROM EvaluationReport) AS reports,
                   (SELECT COUNT(*) FROM EvaluationScore) AS scores
            """
        )
        return cursor.fetchone()


def delete_test_evaluation(report_id):
    with database_cursor(write=True) as cursor:
        cursor.execute("SELECT evaluator_id FROM EvaluationReport WHERE report_id = %s", (report_id,))
        evaluator_id = cursor.fetchone()["evaluator_id"]
        cursor.execute("DELETE FROM EvaluationScore WHERE report_id = %s", (report_id,))
        cursor.execute("DELETE FROM EvaluationReport WHERE report_id = %s", (report_id,))
        cursor.execute("DELETE FROM Evaluator WHERE evaluator_id = %s", (evaluator_id,))


def remove_test_trigger():
    with database_cursor(write=True) as cursor:
        cursor.execute("DROP TRIGGER softreview_test_fail_score")


@unittest.skipUnless(os.getenv("SOFTREVIEW_TEST_MYSQL") == "1", "Isolated MySQL test disabled")
class MySQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.getenv("DB_NAME") != "softreview_test":
            raise RuntimeError("MySQL tests require the isolated softreview_test database.")

    def setUp(self):
        self.client = app.test_client()

    def test_software_returns_joined_catalog_in_id_order(self):
        response = self.client.get("/api/software")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual([row["software_id"] for row in payload["data"]], [1, 2, 3, 4])
        self.assertEqual(payload["data"][0], {
            "software_id": 1,
            "brand_id": 1,
            "brand_name": "Atlas",
            "product_type_id": 1,
            "type_name": "Editor",
        })

    def test_each_allowed_table_returns_rows(self):
        tables = self.client.get("/api/tables").get_json()["data"]
        for name in tables:
            with self.subTest(table=name):
                response = self.client.get(f"/api/tables/{name}")
                self.assertEqual(response.status_code, 200)
                self.assertIsInstance(response.get_json()["data"], list)
        rows = self.client.get("/api/tables/Brand").get_json()["data"]
        self.assertEqual(rows[0], {"brand_id": 1, "brand_name": "Atlas"})

    def test_criteria_return_canonical_names_and_database_ids(self):
        response = self.client.get("/api/criteria")
        self.assertEqual(response.status_code, 200)
        rows = response.get_json()["data"]
        self.assertEqual(
            [row["criterion_name"] for row in rows],
            ["friendliness", "price", "features", "accuracy"],
        )
        stored_rows = self.client.get("/api/tables/ScoreCriterion").get_json()["data"]
        self.assertEqual(
            {row["criterion_name"]: row["criterion_id"] for row in rows},
            {row["criterion_name"].lower(): row["criterion_id"] for row in stored_rows},
        )

    def test_evaluation_creates_one_evaluator_one_report_and_four_scores(self):
        before = evaluation_counts()
        response = self.client.post("/api/evaluations", json=EVALUATION)
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        report_id = payload["data"]["report_id"]
        self.addCleanup(delete_test_evaluation, report_id)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["software_id"], 1)
        self.assertEqual(evaluation_counts(), {
            "evaluators": before["evaluators"] + 1,
            "reports": before["reports"] + 1,
            "scores": before["scores"] + 4,
        })

        with database_cursor() as cursor:
            cursor.execute(
                """
                SELECT LOWER(c.criterion_name) AS name, e.score_value
                FROM EvaluationScore AS e
                JOIN ScoreCriterion AS c ON c.criterion_id = e.criterion_id
                WHERE e.report_id = %s
                """,
                (report_id,),
            )
            scores = {row["name"]: row["score_value"] for row in cursor.fetchall()}
        expected = {key: value for key, value in EVALUATION.items() if key != "software_id"}
        self.assertEqual(scores, expected)

    def test_invalid_and_unknown_software_evaluations_leave_counts_unchanged(self):
        before = evaluation_counts()
        bad_score = self.client.post("/api/evaluations", json={**EVALUATION, "price": 0})
        missing_software = self.client.post("/api/evaluations", json={**EVALUATION, "software_id": 99999})
        self.assertEqual(bad_score.status_code, 400)
        self.assertEqual(missing_software.status_code, 404)
        self.assertEqual(missing_software.get_json()["error"]["code"], "unknown_software")
        self.assertEqual(evaluation_counts(), before)

    def test_score_insert_failure_rolls_back_evaluator_and_report(self):
        before = evaluation_counts()
        with database_cursor(write=True) as cursor:
            cursor.execute(
                """
                CREATE TRIGGER softreview_test_fail_score BEFORE INSERT ON EvaluationScore
                FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'controlled test failure'
                """
            )
        self.addCleanup(remove_test_trigger)
        with self.assertLogs(app.logger, level="ERROR"):
            response = self.client.post("/api/evaluations", json=EVALUATION)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()["error"]["code"], "database_error")
        self.assertNotIn("controlled test failure", response.get_data(as_text=True))
        self.assertEqual(evaluation_counts(), before)

    def rankings(self, query=""):
        response = self.client.get(f"/api/rankings{query}")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        return [
            (row["software_id"], row["average_score"], row["evaluation_count"])
            for row in payload["data"]
        ]

    def test_ranking_defaults_and_best_order_include_stable_tie(self):
        expected = [(1, 8.0, 2), (3, 8.0, 1), (2, 5.0, 1)]
        self.assertEqual(self.rankings(), expected)
        self.assertEqual(self.rankings("?n=5&order=best"), expected)

    def test_worst_ranking_and_limit(self):
        self.assertEqual(self.rankings("?n=5&order=worst"), [(2, 5.0, 1), (1, 8.0, 2), (3, 8.0, 1)])
        self.assertEqual(self.rankings("?n=1&order=worst"), [(2, 5.0, 1)])

    def test_ranking_filters_product_type_and_uses_requested_criterion(self):
        self.assertEqual(
            self.rankings("?n=5&order=best&criterion=price&product_type_id=1"),
            [(2, 9.0, 1), (1, 5.0, 2)],
        )
        self.assertEqual(self.rankings("?product_type_id=2"), [(3, 8.0, 1)])
        self.assertEqual(self.rankings("?product_type_id=99999"), [])
