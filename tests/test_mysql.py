import os
import unittest

from app import app


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
