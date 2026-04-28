import unittest

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

    def test_identify_population_question(self) -> None:
        result = identify_intent_and_fields({"question": "What is the population of Germany?"})
        self.assertEqual(result["country_name"], "Germany")
        self.assertEqual(result["requested_fields"], ["population"])
        self.assertTrue(result["intent_supported"])

    def test_identify_currency_question(self) -> None:
        result = identify_intent_and_fields({"question": "What currency does Japan use?"})
        self.assertEqual(result["country_name"], "Japan")
        self.assertEqual(result["requested_fields"], ["currency"])
        self.assertTrue(result["intent_supported"])

    def test_identify_languages_question(self) -> None:
        result = identify_intent_and_fields({"question": "What languages are spoken in India?"})
        self.assertEqual(result["country_name"], "India")
        self.assertEqual(result["requested_fields"], ["languages"])
        self.assertTrue(result["intent_supported"])

    def test_unsupported_question(self) -> None:
        result = identify_intent_and_fields({"question": "Who is the president of Germany?"})
        self.assertFalse(result["intent_supported"])
        self.assertEqual(result["error"], "Unsupported question.")

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

    def test_synthesize_population_answer(self) -> None:
        germany = NormalizedCountryData(
            common_name="Germany",
            population=83491249,
        )

        result = synthesize_answer(
            {
                "selected_country": germany,
                "requested_fields": ["population"],
            }
        )

        self.assertEqual(result["answer"], "Germany - population: 83,491,249")


if __name__ == "__main__":
    unittest.main()
