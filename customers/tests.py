from unittest import TestCase
from fastapi.testclient import TestClient


class APITestCase(TestCase):
    def setUp(self) -> None:
        from main import app
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__()

    def create_customer(self, *args, **kwargs):
        return self.client.post("/customers/", *args, **kwargs)

    def test_create_customer(self):
        """Создание клиента"""

        resp = self.create_customer(json={
            "name": "x"
        })
        self.assertEqual(201, resp.status_code)

        data = resp.json()
        self.assertIn("id", data)
        self.assertEqual("x", data["name"])
        self.assertIn("id", data["account"])
        self.assertEqual(0, data["account"]["balance"])

    def test_create_customer_with_empty_name(self):
        """Создание клиента с пустым именем"""

        resp = self.create_customer(json={
            "name": ""
        })
        self.assertEqual(400, resp.status_code)

    def test_create_customer_with_long_name(self):
        """Создание клиента с иминем больше 64 симоволов"""

        resp = self.create_customer(json={
            "name": "x" * 65
        })
        self.assertEqual(400, resp.status_code)
