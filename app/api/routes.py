from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


from app.graph.workflow import build_workflow
from app.models.schema import AskRequest,AskResponse,ErrorInfo

router = APIRouter()
workflow = build_workflow()
INDEX_FILE = Path(__file__).resolve().parents[2] / "templates" / "index.html"


def get_error_code(message: str) -> str:
    lowered = message.lower()

    if "unsupported" in lowered:
        return "UNSUPPORTED_QUESTION"
    if "not found" in lowered:
        return "COUNTRY_NOT_FOUND"
    if "ambiguous" in lowered:
        return "AMBIGUOUS_COUNTRY"
    if "identify the country" in lowered:
        return "COUNTRY_IDENTIFICATION_FAILED"
    if "llm service is not configured" in lowered:
        return "LLM_NOT_CONFIGURED"
    if "llm intent extraction failed" in lowered:
        return "LLM_INTENT_EXTRACTION_FAILED"
    if "llm answer synthesis failed" in lowered:
        return "LLM_ANSWER_SYNTHESIS_FAILED"

    return "GRAPH_ERROR"



@router.get("/health")
async def healthcheck():
    return{"status":"ok"}


@router.get("/")
async def index() -> FileResponse:
    return FileResponse(INDEX_FILE)


@router.post("/ask", response_model=AskResponse)
async def ask_country_question(request: AskRequest) -> AskResponse:
    result = await workflow.ainvoke({"question": request.question})
    graph_error = result.get("error")

    if graph_error:
        return AskResponse(
            answer=graph_error,
            country=result.get("selected_country").common_name if result.get("selected_country") else None,
            requested_fields=result.get("requested_fields", []),
            grounded=False,
            source="restcountries",
            error=ErrorInfo(
                code=get_error_code(graph_error),
                message=graph_error,
            ),
        )

    return AskResponse(
        answer=result.get("answer", ""),
        country=result.get("selected_country").common_name if result.get("selected_country") else None,
        requested_fields=result.get("requested_fields", []),
        grounded=True,
        source="restcountries",
        error=None,
    )
