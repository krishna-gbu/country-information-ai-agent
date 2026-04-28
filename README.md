# Country Information AI Agent

Production-style country question answering service built with:

- `FastAPI`
- `LangGraph`
- `REST Countries API`

The app answers grounded questions about country data such as:

- `What is the population of Germany?`
- `What currency does Japan use?`
- `What is the capital and population of Brazil?`

## Assignment Fit

This implementation satisfies the core assignment requirements:

- uses `LangGraph`, not a single prompt
- includes:
  - intent / field identification
  - tool invocation
  - answer synthesis
- uses only the public REST Countries API
- no authentication
- no database
- no embeddings
- no RAG

## Current Capabilities

Supported fields:

- `capital`
- `population`
- `currency`
- `languages`
- `region`
- `subregion`

Supported behaviors:

- valid country questions
- multi-field questions like capital + population
- invalid country handling
- unsupported question handling
- ambiguous country handling such as `Congo`

## Architecture

Runtime flow:

```text
Client
  -> FastAPI route
  -> LangGraph workflow
     -> validate_input
     -> identify_intent_and_fields
     -> fetch_country_data
     -> resolve_match_or_error
     -> synthesize_answer
  -> typed API response
```

Project structure:

```text
app/
  api/        HTTP routes
  graph/      LangGraph state, nodes, workflow
  models/     request / response / internal schemas
  services/   business service layer
  tools/      REST Countries API integration
templates/
  index.html  simple browser UI
tests/
  test_api.py
  test_nodes.py
docs/
  architecture.md
  assignment-constraints.md
  demo-walkthrough.md
  implementation-plan.md
  implementation-qa.md
```

## Local Run

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
uvicorn app.main:app --reload
```

4. Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`

## API Examples

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Population:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the population of Germany?"}'
```

Currency:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What currency does Japan use?"}'
```

Invalid country:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the population of Wakanda?"}'
```

## Testing

Run:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Deployment

Two deployment options are already prepared:

### Render

- `render.yaml` included
- build command:
  - `pip install -r requirements.txt`
- start command:
  - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Docker

Build:

```bash
docker build -t country-information-ai-agent .
```

Run:

```bash
docker run -p 8000:8000 country-information-ai-agent
```

## Known Limitations

- intent extraction is deterministic and pattern-based, not LLM-based
- unsupported phrasing outside handled patterns may fail country extraction
- answers are limited to fields exposed by REST Countries
- hosting link and walkthrough video still need to be created outside this environment

## Useful Docs

- [Architecture](docs/architecture.md)
- [Assignment Constraints](docs/assignment-constraints.md)
- [Demo Walkthrough](docs/demo-walkthrough.md)
- [Implementation Plan](docs/implementation-plan.md)
