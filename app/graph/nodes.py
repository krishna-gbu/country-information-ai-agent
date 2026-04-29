from app.graph.state import AgentState
from app.services.country_service import CountryService
from app.services.llm_service import OpenAIService


def validate_input(state: AgentState) -> AgentState:
    question = state.get("question", "").strip()
    if not question:
        return {"error": "Question is required"}
    return {"question": question}


def _fallback_identify_intent_and_fields(question: str) -> AgentState:
    cleaned_question = (
        question.replace("?", " ")
        .replace("!", " ")
        .replace(".", " ")
        .strip()
    )
    lower_question = " ".join(cleaned_question.lower().split())

    requested_fields = []

    if "capital" in lower_question:
        requested_fields.append("capital")
    if "population" in lower_question or "jansankhya" in lower_question:
        requested_fields.append("population")
    if "currency" in lower_question or "currencies" in lower_question:
        requested_fields.append("currency")
    if "language" in lower_question or "languages" in lower_question or "bhasha" in lower_question:
        requested_fields.append("languages")
    if "region" in lower_question:
        requested_fields.append("region")
    if "subregion" in lower_question:
        requested_fields.append("subregion")

    if not requested_fields:
        return {
            "intent_supported": False,
            "error": "Unsupported question.",
        }

    country_name = ""
    if " of " in lower_question:
        country_name = cleaned_question.rsplit(" of ", 1)[1].strip()
    elif " does " in lower_question and lower_question.endswith(" use"):
        start = lower_question.index(" does ") + len(" does ")
        end = lower_question.rindex(" use")
        country_name = cleaned_question[start:end].strip()
    elif " in " in lower_question:
        country_name = cleaned_question.rsplit(" in ", 1)[1].strip()
    else:
        for separator in (" ke ", " ki ", " ka "):
            if separator in lower_question:
                country_name = cleaned_question.split(separator, 1)[0].strip()
                break

    if not country_name:
        return {
            "intent_supported": False,
            "error": "Could not identify the country.",
        }

    return {
        "country_name": country_name,
        "requested_fields": requested_fields,
        "intent_supported": True,
    }


def _fallback_synthesize_answer(selected_country, requested_fields: list[str]) -> str | None:
    parts = []

    for field in requested_fields:
        if field == "capital":
            value = ", ".join(selected_country.capital) if selected_country.capital else "not available"
            parts.append(f"capital: {value}")
        elif field == "population":
            value = (
                f"{selected_country.population:,}"
                if selected_country.population is not None
                else "not available"
            )
            parts.append(f"population: {value}")
        elif field == "currency":
            value = ", ".join(selected_country.currencies) if selected_country.currencies else "not available"
            parts.append(f"currency: {value}")
        elif field == "languages":
            value = ", ".join(selected_country.languages) if selected_country.languages else "not available"
            parts.append(f"languages: {value}")
        elif field == "region":
            value = selected_country.region if selected_country.region else "not available"
            parts.append(f"region: {value}")
        elif field == "subregion":
            value = selected_country.subregion if selected_country.subregion else "not available"
            parts.append(f"subregion: {value}")

    if not parts:
        return None

    return f"{selected_country.common_name} - " + "; ".join(parts)


async def identify_intent_and_fields(state: AgentState) -> AgentState:
    question = state.get("question", "").strip()
    llm_service = OpenAIService()

    if llm_service.is_configured:
        try:
            extracted = await llm_service.extract_intent(question)
        except Exception:
            extracted = None

        if extracted is not None:
            requested_fields = list(dict.fromkeys(extracted.requested_fields))

            if not extracted.supported:
                return {
                    "country_name": extracted.country_name or "",
                    "requested_fields": requested_fields,
                    "intent_supported": False,
                    "error": extracted.reason_if_unsupported or "Unsupported question.",
                }

            country_name = (extracted.country_name or "").strip().rstrip("?.")
            if not country_name:
                return {
                    "requested_fields": requested_fields,
                    "intent_supported": False,
                    "error": "Could not identify the country.",
                }

            return {
                "country_name": country_name,
                "requested_fields": requested_fields,
                "intent_supported": True,
            }

    return _fallback_identify_intent_and_fields(question)


async def fetch_country_data(state: AgentState) -> AgentState:
    if state.get("error"):
        return {}

    if not state.get("intent_supported"):
        return {}

    country_name = state.get("country_name")
    if not country_name:
        return {"error": "Country name is missing."}

    service = CountryService()
    country_candidates = await service.lookup_by_name(country_name)

    return {"country_candidates": country_candidates}


def resolve_match_or_error(state: AgentState) -> AgentState:
    if state.get("error"):
        return {}

    country_candidates = state.get("country_candidates", [])
    country_name = state.get("country_name", "").strip().lower()

    if not country_candidates:
        return {"error": "Country not found."}

    exact_matches = [
        candidate
        for candidate in country_candidates
        if candidate.common_name.lower() == country_name
        or (candidate.official_name and candidate.official_name.lower() == country_name)
    ]

    if len(exact_matches) == 1:
        return {"selected_country": exact_matches[0]}

    if len(country_candidates) == 1:
        return {"selected_country": country_candidates[0]}

    matched_names = ", ".join(candidate.common_name for candidate in country_candidates[:5])
    return {"error": f"Ambiguous country name. Matches found: {matched_names}."}


async def synthesize_answer(state: AgentState) -> AgentState:
    if state.get("error"):
        return {}

    selected_country = state.get("selected_country")
    requested_fields = state.get("requested_fields", [])

    if not selected_country:
        return {"error": "No country data available for answer synthesis."}

    llm_service = OpenAIService()
    if llm_service.is_configured:
        try:
            llm_answer = await llm_service.synthesize_answer(
                question=state.get("question", ""),
                selected_country=selected_country,
                requested_fields=requested_fields,
            )
        except Exception:
            llm_answer = None

        if llm_answer:
            return {"answer": llm_answer}

    answer = _fallback_synthesize_answer(selected_country, requested_fields)
    if not answer:
        return {"error": "No supported fields available for answer synthesis."}

    return {"answer": answer}
