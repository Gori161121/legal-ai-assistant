# Legal Intake Platform

![CI](https://github.com/Gori161121/legal-ai-assistant/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11-blue)

An AI-assisted client intake system for a law firm. When someone contacts the
firm, a conversational agent captures their details and matter, triages it,
routes it to the right lawyer and offers to book a consultation — then the
client tracks everything in a portal while lawyers work from a dashboard.

The assistant handles **intake and general information only — it does not give
legal advice** (that would be unauthorised practice of law). This boundary is
built into every response.

> This project is deliberately built differently from a plain REST+dashboard
> service: it centres on a **conversational state machine**, a **retrieval (RAG)**
> knowledge base and a **server-rendered web UI** (Jinja2) rather than a JSON-only
> API with a Streamlit front end.

## How it works

```
Client (phone / web / whatsapp)
      ↓
AI intake agent (conversational state machine)
      ↓
Triage  →  Conflict check  →  Lawyer routing
      ↓
Consultation scheduling
      ↓
Structured hand-off to the lawyer  +  client portal + notifications
```

## Highlights

- **Conversational intake agent** — a finite-state dialog that collects the
  client's details, classifies the matter and offers to book a consultation.
- **Retrieval (RAG)** — answers general questions from a legal FAQ knowledge
  base using dependency-free TF-IDF ranking, always with a "not legal advice" note.
- **Triage & lead scoring** — practice-area classification, urgency, complexity
  and a lead-quality score so the firm prioritises the right matters.
- **Conflict-of-interest check** — flags a new client against existing intakes.
- **Routing & scheduling** — assigns the best-matching lawyer by area and
  workload, proposes clash-free consultation slots.
- **Client portal (server-rendered)** — case-stage pipeline, appointment,
  document checklist and notifications.
- **Lawyer dashboard (server-rendered)** — intake queue by lead score,
  practice-area demand and follow-up list.
- **Firm analytics** — funnel conversion, channel mix, practice-area demand.

## Running it

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload      # run from the repo root
```

- Landing page: `http://localhost:8000/`
- Lawyer dashboard: `http://localhost:8000/dashboard`
- Client portal: `http://localhost:8000/portal/1`
- API docs: `http://localhost:8000/docs`

With Docker:

```bash
docker compose up --build
```

## Try the intake agent

```bash
# start a session
curl -s -X POST localhost:8000/intake/chat -H 'content-type: application/json' -d '{}'
# then reply step by step using the returned session_id
curl -s -X POST localhost:8000/intake/chat -H 'content-type: application/json' \
  -d '{"session_id":"<id>","message":"I need help with a divorce"}'
```

## Key endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/intake/chat` | Conversational AI intake agent |
| GET | `/intake/{id}/triage` | Practice area, urgency, lead score |
| GET | `/intake/{id}/summary` | AI hand-off summary for the lawyer |
| GET | `/intake/{id}/routing` | Suggested lawyer |
| GET | `/intake/{id}/slots` | Proposed consultation slots |
| GET | `/intake/{id}/documents` | Document checklist status |
| POST | `/conflict-check` | Conflict-of-interest check |
| GET | `/knowledge/search?q=` | RAG over the legal FAQ |
| GET | `/pipeline` | Case pipeline overview |
| GET | `/stale` | Intakes awaiting follow-up |
| GET | `/analytics` | Firm analytics |
| GET | `/dashboard` | Lawyer dashboard (HTML) |
| GET | `/portal/{id}` | Client portal (HTML) |

## Project layout

```
backend/
  main.py               FastAPI app: API + conversation + server-rendered pages
  data_loader.py        data + knowledge-base boundary
  data_generator.py     deterministic sample-data generator
  data/                 intakes, lawyers, appointments, documents, legal FAQ
  services/             intake, triage, routing, scheduling, conflict, documents,
                        notifications, RAG, conversation, AI summary, analytics
  templates/            Jinja2 pages (landing, dashboard, portal)
tests/                  pytest (services + API + pages)
```

## Tests

```bash
PYTHONPATH=. pytest -q
```

## Roadmap

- Voice intake (phone) via a speech-to-text gateway
- Real SMS/email delivery integration
- Vector embeddings for the knowledge base
- Persist intakes in PostgreSQL (schema in `database/`)

## License

MIT — see [LICENSE](LICENSE).
