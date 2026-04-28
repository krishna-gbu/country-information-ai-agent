# Architecture

## Goal

Answer country questions using public data from REST Countries through a production-shaped LangGraph service.

## High-Level Flow

```text
User -> FastAPI -> LangGraph Workflow -> REST Countries API -> LangGraph Synthesis -> Response
```

## Implemented Components

### API Layer

Responsibility:

- receive user questions
- validate request shape
- call the compiled LangGraph workflow
- return a typed response

Implemented endpoint:

- `POST /ask`

Support endpoints:

- `GET /health`
- `GET /`

### LangGraph Layer

Responsibility:

- orchestrate the agent as a graph instead of a single prompt
- keep state explicit and inspectable
- enforce deterministic behavior for success and failure paths

Current nodes:

1. `validate_input`
2. `identify_intent_and_fields`
3. `fetch_country_data`
4. `resolve_match_or_error`
5. `synthesize_answer`

Current behavior:

- invalid request
- unsupported question
- ambiguous country match
- upstream data failure via HTTP exception
- successful grounded answer

### Tool Layer

Responsibility:

- call `https://restcountries.com/v3.1/name/{country}`
- normalize raw API output into a smaller internal structure
- isolate retry, timeout, and error handling

### Service Layer

Responsibility:

- hold business rules that do not belong in the HTTP route or raw tool wrapper
- optionally convert raw country records into field-focused data for the graph

## Supported Field Strategy

Current supported fields:

- `capital`
- `population`
- `currency`
- `region`
- `subregion`
- `languages`

## State Design

Current graph state fields:

- `question`
- `country_name`
- `requested_fields`
- `intent_supported`
- `country_candidates`
- `selected_country`
- `answer`
- `error`

## Error Handling Strategy

### Invalid country

Example:

- user asks about `Wakanda`

Behavior:

- return a grounded failure message instead of hallucinating

### Ambiguous country

Example:

- user asks about `Congo`

Behavior:

- return a clear ambiguity message listing matched country names

### Unsupported intent

Example:

- `Who is the president of Germany?`

Behavior:

- explain that the service only supports data exposed by REST Countries

### Missing field

Behavior:

- explain that the country was found but the requested field is unavailable

## Production Notes

- keep country facts grounded only in tool data
- keep the graph small and deterministic
- prefer explicit field mapping over open-ended extraction
- typed request and response contracts are used throughout the API
