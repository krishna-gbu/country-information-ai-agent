from typing import TypedDict
from app.models.schema import NormalizedCountryData

class AgentState(TypedDict, total=False):
    question: str
    country_name: str
    requested_fields: list[str]
    intent_supported: bool
    country_candidates: list[NormalizedCountryData]
    selected_country: NormalizedCountryData
    answer: str
    error: str
