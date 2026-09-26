#!/usr/bin/env python3
"""
ask_ekiti_retrieval.py: retrieval + grounded-answer assembly for Ask Ekiti.

Implements spec A9 (answer rules) on top of kb_chunks.jsonl (from kb_chunk.py,
v2 -- chunks now carry per-fact source_ids/source_titles, not the whole
document's source list).

This module has NO dependency on the final embeddings provider or pgvector:
it defines a Retriever interface and ships one working implementation
(keyword overlap scoring, stdlib only) so the answer pipeline, citation
formatting, insufficient-knowledge and conflict logic can be built, tested
and reviewed now. When Member 2 confirms the embeddings provider and
pgvector is available, swap in an EmbeddingRetriever that implements the
same interface (see the "score(query, chunks)" contract below); nothing
else in this file changes.

Known limitation, flagged deliberately rather than hidden: answer_question()
below assembles an answer by concatenating the retrieved chunk texts. That
is a deterministic, inspectable baseline for testing the retrieval and
citation logic end to end -- it is NOT an LLM-grounded answer generator.
The production Ask Ekiti pipeline is expected to replace the concatenation
step with a call to an LLM that is instructed to answer only from the
supplied chunks (spec A9.1-A9.2), while keeping this function's retrieval,
threshold, conflict-detection and citation-formatting logic unchanged.

Conflict detection (v2, fixes a v1 bug flagged in review): v1 grouped
chunks by (category, chunk_type) and flagged a conflict whenever two chunks
in the same group contained different numbers -- so two unrelated facts in
the same category (e.g. "created in 1996" and "has 16 LGAs") could be
wrongly flagged as disagreeing. v2 only compares two chunks when they look
like they're making the SAME claim: their non-numeric wording is highly
similar (Jaccard over words with digits removed) AND they contain different
numbers. This still can't understand meaning the way a human reviewer can
(spec A6 conflict resolution is still a human, Verification Lead, decision)
-- it is a conservative recall aid to surface likely duplicate-claim
conflicts for that review, not a semantic guarantee.

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

# ---------------------------------------------------------------- config
RELEVANCE_THRESHOLD = 0.15   # A9.4: below this, answer "insufficient" rather than guess
SAME_CLAIM_THRESHOLD = 0.5   # word-overlap (numbers removed) above which two chunks are
                              # treated as competing versions of the same claim (A6)
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
    """Stdlib-only baseline: Jaccard word-overlap. Good enough to test the
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
            # Jaccard, not overlap/len(query): a long chunk that only shares
            # one common word (e.g. the place name) with the query should
            # not outscore a short, tightly on-topic chunk.
            out.append((c, overlap / union if union else 0.0))
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
_WORD_RE = re.compile(r"[a-zA-Z']+")
_NUM_RE = re.compile(r"\d[\d,.]*")


def _claim_signature(text):
    """Words only, numbers stripped: two chunks with a high-overlap
    signature are plausibly stating the same underlying claim."""
    return set(w.lower() for w in _WORD_RE.findall(text) if len(w) > 1)


def _numbers(text):
    return tuple(sorted(set(_NUM_RE.findall(text))))


def find_conflicts(top_chunks):
    """Return a list of (chunk_a, chunk_b) pairs that look like the same
    claim stated with different numbers, across different documents.
    Conservative by design: same-document chunks are never compared (a
    single verified document is not internally in conflict with itself),
    and the wording overlap threshold is fairly high."""
    pairs = []
    for i in range(len(top_chunks)):
        for j in range(i + 1, len(top_chunks)):
            a, b = top_chunks[i], top_chunks[j]
            if a.get("doc_id") == b.get("doc_id"):
                continue
            na, nb = _numbers(a["text"]), _numbers(b["text"])
            if not na or not nb or na == nb:
                continue
            sig_a, sig_b = _claim_signature(a["text"]), _claim_signature(b["text"])
            if not sig_a or not sig_b:
                continue
            overlap = len(sig_a & sig_b) / len(sig_a | sig_b)
            if overlap >= SAME_CLAIM_THRESHOLD:
                pairs.append((a, b))
    return pairs


# ---------------------------------------------------------------- answer assembly
def format_citation(chunk):
    return {
        "doc_id": chunk["doc_id"],
        "source_ids": [s for s in chunk.get("source_ids", "").split(";") if s],
        "source_titles": chunk.get("source_titles", ""),
        "tier": chunk.get("tier", ""),
        "last_verified": chunk.get("last_verified", ""),
        "path": chunk.get("path", ""),
    }


def answer_question(question, chunks, retriever=None, language="en",
                     threshold=RELEVANCE_THRESHOLD, top_k=TOP_K):
    """Implements spec A9. Returns a dict matching the agreed API contract:
    {answer, answer_status, language, citations}. Pure function: no I/O,
    no network. Caller supplies the chunk list (from kb_chunks.jsonl) and,
    later, the real retriever.

    NOTE (see module docstring): "answer" below is assembled by
    concatenating retrieved chunk text, not by an LLM. This is intentional
    for this foundation stage; do not present it to users as final-quality
    generation without the LLM step described above.
    """
    retriever = retriever or KeywordRetriever()
    scored = retriever.score(question, chunks)
    scored.sort(key=lambda x: x[1], reverse=True)
    top = [c for c, s in scored if s >= threshold][:top_k]

    if not top:
        insufficient = INSUFFICIENT_EN if language != "yo" else INSUFFICIENT_YO
        return {"answer": insufficient, "answer_status": "insufficient",
                "language": language, "citations": []}

    conflicts = find_conflicts(top)
    if conflicts:
        involved = {id(c) for pair in conflicts for c in pair}
        conflicting = [c for c in top if id(c) in involved]
        parts = [f"- {c['text']} (source {c.get('source_ids', '?')}, "
                 f"tier {c.get('tier', '?')})" for c in conflicting]
        answer = "Sources differ on this. What's recorded:\n" + "\n".join(parts)
        return {"answer": answer, "answer_status": "conflict", "language": language,
                "citations": [format_citation(c) for c in conflicting]}

    lines = [c["text"] for c in top]
    answer = " ".join(lines)
    return {"answer": answer, "answer_status": "answered", "language": language,
            "citations": [format_citation(c) for c in top]}


# ---------------------------------------------------------------- selftest
def selftest():
    chunks = [
        {"chunk_id": "a#001", "doc_id": "a", "chunk_type": "fact",
         "text": "Ekiti State was created on 1 October 1996.",
         "source_ids": "SRC-001", "source_titles": "Creation statement",
         "category": "history", "tier": "A", "last_verified": "2026-09-21",
         "path": "01_History/a.md"},
        {"chunk_id": "a#002", "doc_id": "a", "chunk_type": "fact",
         "text": "Ekiti State has 16 local government areas.",
         "source_ids": "SRC-004", "source_titles": "Constitution",
         "category": "history", "tier": "A", "last_verified": "2026-09-21",
         "path": "01_History/a.md"},
        {"chunk_id": "b#001", "doc_id": "b", "chunk_type": "fact",
         "text": "Ekiti State's 2006 census population was 2,384,212.",
         "source_ids": "SRC-003", "source_titles": "State government page",
         "category": "statistics", "tier": "A", "last_verified": "2026-09-21",
         "path": "09_Statistics/b.md"},
        {"chunk_id": "c#001", "doc_id": "c", "chunk_type": "fact",
         "text": "Ekiti State's 2006 census population was 2,398,957.",
         "source_ids": "SRC-008", "source_titles": "NPC priority table",
         "category": "statistics", "tier": "A", "last_verified": "2026-09-21",
         "path": "09_Statistics/c.md"},
    ]
    failures = []

    r1 = answer_question("When was Ekiti State created?", chunks)
    if r1["answer_status"] != "answered":
        failures.append(f"expected 'answered', got {r1['answer_status']}: {r1['answer']!r}")
    if not r1["citations"] or r1["citations"][0]["doc_id"] != "a":
        failures.append(f"expected citation to doc 'a', got {r1['citations']}")
    if r1["citations"] and r1["citations"][0]["source_titles"] != "Creation statement":
        failures.append("citation should carry the per-fact source_titles")

    r1b = answer_question("How many local government areas does Ekiti have?", chunks)
    if r1b["answer_status"] == "conflict":
        failures.append("unrelated facts in the same category (creation date, LGA count) "
                         "must not be flagged as conflicting")

    r2 = answer_question("What is the population of Mars?", chunks)
    if r2["answer_status"] != "insufficient":
        failures.append(f"expected 'insufficient', got {r2['answer_status']}")
    if r2["citations"]:
        failures.append("insufficient answers must carry no citations")

    r3 = answer_question("What was the 2006 census population?", chunks)
    if r3["answer_status"] != "conflict":
        failures.append(f"expected 'conflict' for the two disagreeing population chunks, "
                         f"got {r3['answer_status']}")
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
    if not scored or max(s for _, s in scored) <= 0:
        failures.append("keyword retriever should score an on-topic chunk above zero")

    same_doc = [chunks[2], {**chunks[2], "chunk_id": "b#002", "text": "The 2006 population was 2,999,999."}]
    if find_conflicts(same_doc):
        failures.append("chunks from the same document must never be flagged as conflicting")

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print("SELFTEST PASSED (7 answer-assembly/conflict cases + keyword scoring check)")
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
