# Implementation Plan

## Step 1: Pick the LLM Provider

Choose one provider before coding the graph.

Practical default:

- `langchain-openai`
- a smaller fast model for extraction and synthesis

Alternative:

- `langchain-anthropic`

Keep the provider behind one small adapter so it is easy to swap later.

## Step 2: Define Schemas

Implement:

- request schema for `POST /ask`
- response schema returned to the client
- internal schema for extracted intent
- internal schema for normalized country data

## Step 3: Implement the REST Countries Tool

Build one wrapper that:

- accepts a country name
- calls `GET /v3.1/name/{country}`
- times out cleanly
- normalizes output
- raises controlled errors

Normalization should flatten fields you care about, such as:

- common name
- official name
- capital
- population
- currencies
- languages
- region
- subregion
- timezones
- area

## Step 4: Implement LangGraph Nodes

Recommended node responsibilities:

### `validate_input`

- reject empty questions
- normalize whitespace

### `identify_intent_and_fields`

- extract the country name
- map the user question to supported fields
- mark unsupported questions

### `fetch_country_data`

- call the tool only when the question is supported and the country is extracted

### `resolve_match_or_error`

- handle zero matches
- handle multiple matches
- choose one clear record when possible

### `synthesize_answer`

- produce a concise answer only from normalized tool data

### `format_response`

- shape the final JSON response

## Step 5: Wire the Graph

Expected routing:

- invalid input -> format error response
- unsupported intent -> format unsupported response
- valid extraction -> tool call
- tool success -> synthesis
- tool failure -> format failure response

## Step 6: Connect the API

`POST /ask` should:

- validate the incoming payload
- invoke the compiled graph
- return the final typed response

## Step 7: Add Tests

Minimum useful test set:

- valid single-field question
- valid multi-field question
- invalid country
- ambiguous country
- unsupported question
- missing field
- upstream timeout

## Step 8: Add a Small Frontend

Keep it simple:

- one text input
- one submit button
- one response panel

Do not overbuild the UI. The assignment is evaluating the agent design, not frontend complexity.

## Step 9: Deploy

Recommended path:

- deploy the FastAPI app and small UI together on Render

Public deliverable:

- one URL to test the app directly
- README with setup and architecture
- short walkthrough video
