from langgraph.graph import START, END, StateGraph
from app.graph.state import AgentState

from app.graph.nodes import(
    validate_input,
    identify_intent_and_fields,
    fetch_country_data,
    resolve_match_or_error,
    synthesize_answer
)


def build_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("validate_input", validate_input)
    graph.add_node("identify_intent_and_fields", identify_intent_and_fields)
    graph.add_node("fetch_country_data", fetch_country_data)
    graph.add_node("resolve_match_or_error", resolve_match_or_error)
    graph.add_node("synthesize_answer", synthesize_answer)

    graph.add_edge(START, "validate_input")
    graph.add_edge("validate_input", "identify_intent_and_fields")
    graph.add_edge("identify_intent_and_fields", "fetch_country_data")
    graph.add_edge("fetch_country_data", "resolve_match_or_error")
    graph.add_edge("resolve_match_or_error", "synthesize_answer")
    graph.add_edge("synthesize_answer", END)

    return graph.compile()


