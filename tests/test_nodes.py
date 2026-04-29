import unittest
from unittest.mock import AsyncMock, patch

from app.graph.nodes import (
    identify_intent_and_fields,
    resolve_match_or_error,
    synthesize_answer,
    validate_input,
)
from app.models.schema import NormalizedCountryData


class TestGraphNodes(unittest.TestCase):
    def test_validate_input_trims_question(self) -> None:
        result = validate_input({"question": "  What is the population of Germany?  "})
        self.assertEqual(result, {"question": "What is the population of Germany?"})

    def test_resolve_ambiguous_country(self) -> None:
        dr_congo = NormalizedCountryData(common_name="DR Congo")
        republic_of_congo = NormalizedCountryData(common_name="Republic of the Congo")

        result = resolve_match_or_error(
            {
                "country_name": "Congo",
                "country_candidates": [dr_congo, republic_of_congo],
            }
        )

        self.assertIn("Ambiguous country name.", result["error"])


class TestGraphAsyncNodes(unittest.IsolatedAsyncioTestCase):
    @patch("app.graph.nodes.OpenAIService")
    async def test_identify_population_question(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.extract_intent = AsyncMock(
            return_value=type(
                "Intent",
                (),
                {
                    "country_name": "Germany",
                    "requested_fields": ["population"],
                    "supported": True,
                    "reason_if_unsupported": None,
                },
            )()
        )
        result = await identify_intent_and_fields({"question": "What is the population of Germany?"})
        self.assertEqual(result["country_name"], "Germany")
        self.assertEqual(result["requested_fields"], ["population"])
        self.assertTrue(result["intent_supported"])

    @patch("app.graph.nodes.OpenAIService")
    async def test_identify_currency_question(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.extract_intent = AsyncMock(
            return_value=type(
                "Intent",
                (),
                {
                    "country_name": "Japan",
                    "requested_fields": ["currency"],
                    "supported": True,
                    "reason_if_unsupported": None,
                },
            )()
        )
        result = await identify_intent_and_fields({"question": "What currency does Japan use?"})
        self.assertEqual(result["country_name"], "Japan")
        self.assertEqual(result["requested_fields"], ["currency"])
        self.assertTrue(result["intent_supported"])

    @patch("app.graph.nodes.OpenAIService")
    async def test_identify_languages_question(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.extract_intent = AsyncMock(
            return_value=type(
                "Intent",
                (),
                {
                    "country_name": "India",
                    "requested_fields": ["languages"],
                    "supported": True,
                    "reason_if_unsupported": None,
                },
            )()
        )
        result = await identify_intent_and_fields({"question": "What languages are spoken in India?"})
        self.assertEqual(result["country_name"], "India")
        self.assertEqual(result["requested_fields"], ["languages"])
        self.assertTrue(result["intent_supported"])

    @patch("app.graph.nodes.OpenAIService")
    async def test_identify_region_and_subregion_question(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.extract_intent = AsyncMock(side_effect=Exception("401"))

        result = await identify_intent_and_fields(
            {"question": "What is the region and subregion of South Africa?"}
        )

        self.assertEqual(result["country_name"], "South Africa")
        self.assertEqual(result["requested_fields"], ["region", "subregion"])
        self.assertTrue(result["intent_supported"])

    @patch("app.graph.nodes.OpenAIService")
    async def test_unsupported_question(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.extract_intent = AsyncMock(
            return_value=type(
                "Intent",
                (),
                {
                    "country_name": "Germany",
                    "requested_fields": [],
                    "supported": False,
                    "reason_if_unsupported": "Unsupported question.",
                },
            )()
        )
        result = await identify_intent_and_fields({"question": "Who is the president of Germany?"})
        self.assertFalse(result["intent_supported"])
        self.assertEqual(result["error"], "Unsupported question.")

    @patch("app.graph.nodes.OpenAIService")
    async def test_synthesize_population_answer(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.synthesize_answer = AsyncMock(return_value="Germany has a population of 83,491,249.")
        germany = NormalizedCountryData(
            common_name="Germany",
            population=83491249,
        )

        result = await synthesize_answer(
            {
                "selected_country": germany,
                "requested_fields": ["population"],
            }
        )

        self.assertEqual(result["answer"], "Germany has a population of 83,491,249.")

    @patch("app.graph.nodes.OpenAIService")
    async def test_fallback_identify_hinglish_question(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.extract_intent = AsyncMock(side_effect=Exception("401"))

        result = await identify_intent_and_fields({"question": "japan ke population batao"})

        self.assertEqual(result["country_name"], "japan")
        self.assertEqual(result["requested_fields"], ["population"])
        self.assertTrue(result["intent_supported"])

    @patch("app.graph.nodes.OpenAIService")
    async def test_fallback_synthesize_when_llm_fails(self, OpenAIServiceMock) -> None:
        service = OpenAIServiceMock.return_value
        service.is_configured = True
        service.synthesize_answer = AsyncMock(side_effect=Exception("401"))
        germany = NormalizedCountryData(
            common_name="Germany",
            population=83491249,
        )

        result = await synthesize_answer(
            {
                "selected_country": germany,
                "requested_fields": ["population"],
            }
        )

        self.assertEqual(result["answer"], "Germany - population: 83,491,249")


if __name__ == "__main__":
    unittest.main()
