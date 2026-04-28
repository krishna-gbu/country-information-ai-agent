import json
import os

import httpx

from app.models.schema import ExtractedIntent, NormalizedCountryData


class OpenAIService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def extract_intent(self, question: str) -> ExtractedIntent | None:
        if not self.is_configured:
            return None

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You extract structured intent from country questions. "
                        "Only support these fields: capital, population, currency, "
                        "languages, region, subregion. "
                        "If the question asks for anything else, set supported to false "
                        "and explain the reason briefly."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "country_question_intent",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "country_name": {
                                "type": ["string", "null"],
                            },
                            "requested_fields": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "capital",
                                        "population",
                                        "currency",
                                        "languages",
                                        "region",
                                        "subregion",
                                    ],
                                },
                            },
                            "supported": {
                                "type": "boolean",
                            },
                            "reason_if_unsupported": {
                                "type": ["string", "null"],
                            },
                        },
                        "required": [
                            "country_name",
                            "requested_fields",
                            "supported",
                            "reason_if_unsupported",
                        ],
                    },
                },
            },
        }

        response_json = await self._post_chat_completion(payload)
        content = response_json["choices"][0]["message"]["content"]
        if not content:
            return None

        return ExtractedIntent.model_validate(json.loads(content))

    async def synthesize_answer(
        self,
        question: str,
        selected_country: NormalizedCountryData,
        requested_fields: list[str],
    ) -> str | None:
        if not self.is_configured:
            return None

        country_data = {
            "common_name": selected_country.common_name,
            "official_name": selected_country.official_name,
            "capital": selected_country.capital,
            "population": selected_country.population,
            "currencies": selected_country.currencies,
            "languages": selected_country.languages,
            "region": selected_country.region,
            "subregion": selected_country.subregion,
        }

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Answer the user's country question using only the supplied facts. "
                        "Do not add facts that are not present in the provided data. "
                        "If a requested field is missing, say it is not available. "
                        "Keep the answer concise and natural."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"Requested fields: {', '.join(requested_fields)}\n"
                        f"Country data: {json.dumps(country_data, ensure_ascii=False)}"
                    ),
                },
            ],
        }

        response_json = await self._post_chat_completion(payload)
        content = response_json["choices"][0]["message"]["content"]
        if not content:
            return None

        return content.strip()

    async def _post_chat_completion(self, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        return response.json()
