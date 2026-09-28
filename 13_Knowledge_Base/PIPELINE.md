# Ask Ekiti data pipeline

`kb_validate.py` generates `kb_manifest.csv` from document front matter. Only
rows with `status=verified` and `ingestible=yes` enter the backend. The current
manifest has no such rows; the API correctly returns insufficient evidence until
the verification team approves documents and regenerates the manifest.

Only content domains 01–09 are eligible. Citizen Stories and Ekiti 2056 are
excluded by the existing Ask Ekiti KB specification. Photographs, source documents,
research notes, media, design, and project documentation are supporting assets,
not direct answer text. `source_ids`, SHA-256, and per-fact `[S#]` markers are
required; a missing or unresolved marker rejects that document. Files cannot
escape the knowledge base root. Changed files replace their chunks; unchanged
hashes are skipped. No document is implicitly promoted from draft to verified.

After review, from the repository root:

```sh
python 13_Knowledge_Base/tools/kb_validate.py --root .
cd backend
alembic upgrade head
python scripts/ingest_knowledge.py
```

Use Postgres with pgvector and the configured 384-dimensional multilingual
MiniLM model. The first local embedding run downloads the model. `POST
/api/ask-ekiti` accepts `{ "question": "...", "category": "history" }`
(`category` optional), returns `answer`, `answer_status`, `language`, and
`citations`. Each citation includes document ID and per-fact source IDs and
titles and URLs. Retrieval filters verified documents and optionally category, orders
by cosine distance, and declines evidence beyond distance 0.65. Answers are
verbatim retrieved facts, not model-generated prose.

The LLM gateway's payload and authentication contract remain to be supplied
by its owner before generation can be connected. A future gateway request
should receive the question and only the selected fact text plus citations;
its output must be checked against those citations before it is shown.
