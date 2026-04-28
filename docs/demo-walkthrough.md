# Video Walkthrough Outline

Keep the video short and structured. A 4 to 7 minute walkthrough is enough.

## 1. Overall Architecture

Show:

- FastAPI entrypoint
- LangGraph workflow
- REST Countries tool wrapper
- simple frontend

Explain:

- LangGraph orchestrates the flow
- intent extraction is deterministic in the current implementation
- the country API is the factual source of truth

## 2. Agent Flow

Walk through the graph using a few examples:

- `What is the population of Germany?`
- `What currency does Japan use?`
- `What is the capital and population of Brazil?`

For each example, explain:

- extracted country
- extracted fields
- tool call
- final grounded answer

## 3. Error and Edge Cases

Demo at least two:

- invalid country like `Wakanda`
- ambiguous input like `Congo`
- unsupported question like `Who is the president of France?`

## 4. Production Behavior

Explain:

- input validation
- typed schemas
- timeout handling
- clean separation of modules

## 5. Known Limitations and Trade-Offs

Say clearly:

- facts are limited to the REST Countries dataset
- the system does not answer leader or current-events questions
- ambiguous names may need clarification
- the current extractor is rule-based, so unusual phrasing may fail
- availability depends on the public API
