# EKITI@30 DIGITAL — Initial Application Architecture

**Owner:** Member 2 — Engineering Lead
**Status:** Proposed (Issue #2)

## Stack

| Layer     | Choice                                   | Why |
|-----------|-------------------------------------------|-----|
| Frontend  | Next.js (TypeScript, App Router)          | File-based routing maps cleanly to the 5 core features; good for content-heavy pages (Timeline, Explore, Knowledge Base); easy for the design lead to work in. |
| Backend   | FastAPI (Python)                          | Fast to scaffold, auto-generated OpenAPI docs (useful with 8 collaborators), natural fit for the AI/data lead's "Ask Ekiti" RAG pipeline (Python's ML/embedding ecosystem). |
| Database  | PostgreSQL (via SQLAlchemy), SQLite for local dev | Structured knowledge-base entries, LGAs, timeline events, and citizen stories all fit relational data well. SQLite fallback removes setup friction in week 1. |
| Dev env   | `.env` files, Docker Compose (optional, backend + db) | One-command local run for non-engineering contributors. |

## Repository layout

```
Ekiti30Digital/
├── backend/
│   ├── app/
│   │   ├── main.py            # entry point, mounts routers
│   │   ├── core/
│   │   │   └── config.py      # env/settings
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── timeline.py
│   │   │       ├── lgas.py
│   │   │       ├── stories.py
│   │   │       ├── vision2056.py
│   │   │       └── ask_ekiti.py
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # business logic, KB ingestion, RAG later
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/app/
│   │   ├── timeline/
│   │   ├── explore/
│   │   ├── my-story/
│   │   ├── ask-ekiti/
│   │   ├── ekiti-2056/
│   │   └── page.tsx            # homepage
│   ├── package.json
│   └── .env.example
├── 01_History/ ... 18_Project_Documentation/   # existing content folders (unchanged)
├── ARCHITECTURE.md
├── CONTRIBUTING.md
└── README.md
```

Content folders (`01_History` … `18_Project_Documentation`) stay as the raw/source material the Knowledge Base and AI/Data leads work from; the backend's `services/` layer is where that content eventually gets ingested into structured data.

## Data flow (high level)

1. Research/content leads add sourced material into the numbered content folders.
2. Knowledge Base structure (Issue #3) defines how that material is modeled.
3. Backend exposes it via REST endpoints (`/api/timeline`, `/api/lgas`, `/api/knowledge-base`, etc.).
4. Frontend pages fetch from those endpoints.
5. `Ask Ekiti` (AI/Data lead) queries the same structured knowledge base rather than an unrestricted model — the backend's `ask_ekiti` route is the integration point.

## Local development

- Backend: `uvicorn app.main:app --reload` (port 8000)
- Frontend: `npm run dev` (port 3000)
- Health check: `GET /api/health` → `{"status": "ok"}`

## Status

This structure is intended to be the **minimum working foundation** for the launch sprint — other members should be able to add routes, models, and pages within it without restructuring.
