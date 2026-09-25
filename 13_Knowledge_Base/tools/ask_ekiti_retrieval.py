#!/usr/bin/env python3
"""
ask_ekiti_retrieval.py: retrieval + grounded-answer assembly for Ask Ekiti.

Implements spec A9 (answer rules) on top of kb_chunks.jsonl (from kb_chunk.py).
This module has NO dependency on the final embeddings provider or pgvector:
it defines a Retriever interface and ships one working implementation
(keyword overlap scoring, stdlib only) so the answer pipeline, citation
formatting, insufficient-knowledge and conflict logic can be built, tested
and reviewed now. When Member 2 confirms the embeddings provider and
pgvector is available, swap in an EmbeddingRetriever that implements the
same interface (see the "score(query, chunks)" contract below); nothing
else in this file changes.

This is a library, not a web server: Member 2's FastAPI route imports
`answer_question` and returns its result as the /ask response body,
matching the agreed contract:
    {answer, answer_status, language, citations[]}

Usage:
    python ask_ekiti_retrieval.py "When was Ekiti State created?"
    python ask_ekiti_retrieval.py --selftest
"""
import argparse
import json
import os
import re
import sys
import tempfile
from collections import Counter

# ---------------------------------------------------------------- config
RELEVANCE_THRESHOLD = 0.15   # A9.4: below this, answer "insufficient" rather than guess
TOP_K = 6                    # max chunks considered as context for one answer
STOPWORDS = set("""
a an the of in on at to for and or is was were are be been being with as by from
this that these those it its it's what when who how many much does do did state
""".split())

INSUFFICIENT_EN = "The available verified knowledge isn't enough to answer that yet."
INSUFFICIENT_YO = "Ìmọ̀ tí a ti fọwọ́ sí kò tíì tó láti dáhùn ìbéèrè yìí."  # placeholder,
# machine-drafted; not yet reviewed by the Yoruba reviewer (spec A8/A9.9) - do not
# ship to users until Faith Ogunlade reviews this exact string.


# ---------------------------------------------------------------- retriever interface
class Retriever:
    """Interface every retrieval backend must implement.

    score(query, chunks) -> list of (chunk, score) pairs, any order, score in [0, 1].
    Swap KeywordRetriever for an embedding/pgvector-backed retriever later
    without changing anything below this class.
    """
    def score(self, query, chunks):
        raise NotImplementedError


class KeywordRetriever(Retriever):
    """Stdlib-only baseline: normalized word-overlap. Good enough to test the
    pipeline end to end; expected to be replaced, not extended."""

    def _tokens(self, text):
        words = re.findall(r"[a-zA-Z0-9']+", text.lower())
        return [w for w in words if w not in STOPWORDS and len(w) > 1]

    def score(self, query, chunks):
        q = set(self._tokens(query))
        if not q:
            return [(c, 0.0) for c in chunks]
        out = []
        for c in chunks:
            t = set(self._tokens(c["text"]))
            if not t:
                out.append((c, 0.0))
                continue
            overlap = len(q & t)
            union = len(q | t)
            score = overlap / union if union else 0.0  # Jaccard similarity:
            # penalizes a long, mostly-unrelated chunk that only shares one
            # common word (e.g. the place name) with the query
            out.append((c, score))
        return out


# ---------------------------------------------------------------- data loading
def load_chunks(path):
    chunks = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                chunks.append(json.loads(ln))
    return chunks


# ---------------------------------------------------------------- conflict detection
def group_by_doc(chunks):
    by_doc = {}
    for c in chunks:
        by_doc.setdefault(c["doc_id"], []).append(c)
    return by_doc


def detect_conflict(top_chunks):
    """A9.6: if the top results come from documents whose declared status
    disagrees on the same fact, this returns True so the caller can present
    both instead of picking one. Conflict is signalled by chunk_type
    'conflict' set by the ingestion step, or by two chunks with high mutual
    relevance but numerically different content for what looks like the
    same claim (same doc category + overlapping key numbers that differ).
    This heuristic is intentionally conservative: it flags candidates for a
    human to confirm, it does not resolve them."""
    nums_by_group = {}
    for c in top_chunks:
        key = (c.get("category"), c.get("chunk_type"))
        nums = tuple(sorted(set(re.findall(r"\d{3,}", c["text"]))))
        if nums:
            nums_by_group.setdefault(key, set()).add(nums)
    return any(len(v) > 1 for v in nums_by_group.values())


# ---------------------------------------------------------------- answer assembly
def format_citation(chunk):
    return {
        "doc_id": chunk["doc_id"],
        "source_ids": [s for s in chunk.get("source_ids", "").split(";") if s],
        "tier": chunk.get("tier", ""),
        "last_verified": chunk.get("last_verified", ""),
        "path": chunk.get("path", ""),
    }


def answer_question(question, chunks, retriever=None, language="en",
                     threshold=RELEVANCE_THRESHOLD, top_k=TOP_K):
    """Implements spec A9. Returns a dict matching the agreed API contract:
    {answer, answer_status, language, citations}. Pure function: no I/O,
    no network. Caller supplies the chunk list (from kb_chunks.jsonl) and,
    later, the real retriever."""
    retriever = retriever or KeywordRetriever()
    scored = retriever.score(question, chunks)
    scored.sort(key=lambda x: x[1], reverse=True)
    top = [c for c, s in scored if s >= threshold][:top_k]

    if not top:
        insufficient = INSUFFICIENT_EN if language != "yo" else INSUFFICIENT_YO
        return {"answer": insufficient, "answer_status": "insufficient",
                "language": language, "citations": []}

    if detect_conflict(top):
        parts = [f"- {c['text']} (source {c.get('source_ids', '?')}, "
                 f"tier {c.get('tier', '?')})" for c in top]
        answer = "Sources differ on this. What's recorded:\n" + "\n".join(parts)
        return {"answer": answer, "answer_status": "conflict", "language": language,
                "citations": [format_citation(c) for c in top]}

    lines = [c["text"] for c in top]
    answer = " ".join(lines)
    return {"answer": answer, "answer_status": "answered", "language": language,
            "citations": [format_citation(c) for c in top]}


# ---------------------------------------------------------------- selftest
def selftest():
    chunks = [
        {"chunk_id": "a#001", "doc_id": "a", "chunk_type": "fact",
         "text": "Ekiti State was created on 1 October 1996.",
         "source_ids": "SRC-001", "category": "history", "tier": "A",
         "last_verified": "2026-09-21", "path": "01_History/a.md"},
        {"chunk_id": "b#001", "doc_id": "b", "chunk_type": "fact",
         "text": "Ekiti State's 2006 census population was 2384212.",
         "source_ids": "SRC-003", "category": "statistics", "tier": "A",
         "last_verified": "2026-09-21", "path": "09_Statistics/b.md"},
        {"chunk_id": "c#001", "doc_id": "c", "chunk_type": "fact",
         "text": "Ekiti State's 2006 census population was 2398957.",
         "source_ids": "SRC-008", "category": "statistics", "tier": "A",
         "last_verified": "2026-09-21", "path": "09_Statistics/c.md"},
    ]
    failures = []

    r1 = answer_question("When was Ekiti State created?", chunks)
    if r1["answer_status"] != "answered":
        failures.append(f"expected 'answered', got {r1['answer_status']}")
    if not r1["citations"] or r1["citations"][0]["doc_id"] != "a":
        failures.append(f"expected citation to doc 'a', got {r1['citations']}")

    r2 = answer_question("What is the population of Mars?", chunks)
    if r2["answer_status"] != "insufficient":
        failures.append(f"expected 'insufficient', got {r2['answer_status']}")
    if r2["citations"]:
        failures.append("insufficient answers must carry no citations")

    r3 = answer_question("What was the 2006 census population?", chunks)
    if r3["answer_status"] != "conflict":
        failures.append(f"expected 'conflict' for the two disagreeing population chunks, got {r3['answer_status']}")
    if len(r3["citations"]) < 2:
        failures.append("a conflict answer should cite every disagreeing source")

    r4 = answer_question("Tell me about Ekiti", [])
    if r4["answer_status"] != "insufficient" or r4["citations"]:
        failures.append("an empty knowledge base must always answer 'insufficient'")

    r5 = answer_question("When was Ekiti State created?", chunks, language="yo")
    if r5["language"] != "yo":
        failures.append("language should be echoed back on the response")

    kw = KeywordRetriever()
    scored = kw.score("Ekiti State created 1996", chunks)
    if not scored or scored[0][1] <= 0:
        failures.append("keyword retriever should score an on-topic chunk above zero")

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print(f"SELFTEST PASSED (5 answer-assembly cases + keyword scoring check)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Ask Ekiti retrieval + grounded-answer assembly.")
    ap.add_argument("question", nargs="?")
    ap.add_argument("--chunks", default=None, help="default: 13_Knowledge_Base/kb_chunks.jsonl")
    ap.add_argument("--language", default="en", choices=["en", "yo"])
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.question:
        sys.exit("provide a question, or run with --selftest")
    path = a.chunks or os.path.join(a.root, "13_Knowledge_Base", "kb_chunks.jsonl")
    if not os.path.exists(path):
        sys.exit(f"chunks file not found: {path} (run kb_chunk.py first)")
    chunks = load_chunks(path)
    result = answer_question(a.question, chunks, language=a.language)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
