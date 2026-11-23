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
