import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_healthcheck(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("app.api.routes.workflow.ainvoke", new_callable=AsyncMock)
    def test_ask_success_response(self, mock_ainvoke: AsyncMock) -> None:
        mock_ainvoke.return_value = {
            "answer": "Germany - population: 83,491,249",
            "requested_fields": ["population"],
            "selected_country": type("Country", (), {"common_name": "Germany"})(),
        }

        response = self.client.post("/ask", json={"question": "What is the population of Germany?"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "answer": "Germany - population: 83,491,249",
                "country": "Germany",
                "requested_fields": ["population"],
                "grounded": True,
                "source": "restcountries",
                "error": None,
            },
        )

    @patch("app.api.routes.workflow.ainvoke", new_callable=AsyncMock)
    def test_ask_error_response(self, mock_ainvoke: AsyncMock) -> None:
        mock_ainvoke.return_value = {
            "error": "Country not found.",
            "requested_fields": ["population"],
        }

        response = self.client.post("/ask", json={"question": "What is the population of Wakanda?"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "answer": "Country not found.",
                "country": None,
                "requested_fields": ["population"],
                "grounded": False,
                "source": "restcountries",
                "error": {
                    "code": "COUNTRY_NOT_FOUND",
                    "message": "Country not found.",
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
