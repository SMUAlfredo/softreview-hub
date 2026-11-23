import unittest
from unittest.mock import patch

from mysql.connector import Error as MySQLError

from app import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_works_without_database_settings(self):
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True, "data": {"status": "ok"}})

    def test_software_reports_missing_database_configuration(self):
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.get("/api/software")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"]["code"], "database_unavailable")

    @patch("app.database_cursor", side_effect=MySQLError("private connector detail"))
    def test_software_redacts_database_errors(self, _cursor):
        with self.assertLogs(app.logger, level="ERROR") as logs:
            response = self.client.get("/api/software")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()["error"]["code"], "database_error")
        self.assertNotIn("private connector detail", response.get_data(as_text=True))
        self.assertNotIn("private connector detail", " ".join(logs.output))

    def test_method_error_preserves_allow_header_and_json_envelope(self):
        response = self.client.post("/api/software")
        self.assertEqual(response.status_code, 405)
        self.assertIn("GET", response.headers["Allow"])
        self.assertEqual(response.get_json()["error"]["code"], "method_not_allowed")

    @patch("app.database_cursor")
    def test_tables_list_and_unknown_table_do_not_connect(self, cursor):
        response = self.client.get("/api/tables")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True, "data": [
            "Brand", "ProductType", "SoftwareSystem", "Evaluator", "EvaluationReport",
            "ScoreCriterion", "EvaluationScore",
        ]})
        response = self.client.get("/api/tables/not_a_project_table")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"]["code"], "unknown_table")
        cursor.assert_not_called()
