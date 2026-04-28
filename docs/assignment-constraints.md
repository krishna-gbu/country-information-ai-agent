# Assignment Constraints Mapping

This document maps each assignment requirement to the current implementation.

## Required

### Use LangGraph, not a single prompt

Current implementation:

- explicit graph state
- separate nodes for extraction, tool call, and answer synthesis
- compiled LangGraph workflow with ordered nodes

### Intent / field identification step

Current implementation:

- `identify_intent_and_fields` node
- extracts:
  - country name
  - requested fields
  - supported or unsupported intent

### Tool invocation step

Current implementation:

- one dedicated tool wrapper for `GET https://restcountries.com/v3.1/name/{country}`
- timeout handling
- response normalization into internal models

### Answer synthesis step

Current implementation:

- `synthesize_answer` node
- final answer composed only from normalized tool output

## Constraints

### No authentication

Current implementation:

- no user login
- no protected backend routes
- no auth required for the country data source

### No database

Current implementation:

- no persistent storage
- no database layer at all

### No embeddings

Current implementation:

- no vectorization layer
- no semantic retrieval

### No RAG

Current implementation:

- no document index
- no chunking
- no retrieval layer beyond the public REST Countries API

## Expected Behavior

### Accurate and grounded answers

Current implementation:

- use REST Countries as the only factual source
- pass normalized tool results into answer synthesis
- do not answer unsupported facts from model memory

### Invalid input and partial data

Current implementation:

- return controlled responses for:
  - invalid country names
  - ambiguous country names
  - unsupported questions
  - missing field values using `not available`
  - upstream API failures through HTTP error propagation

### Structured and maintainable code

Current implementation:

- separate API, graph, models, tools, and services
- typed schemas
- testable node boundaries

### Production-minded design

Current implementation:

- typed request and response contracts
- timeout handling
- automated tests
- deployment config (`Dockerfile`, `render.yaml`)
- browser UI for direct testing
