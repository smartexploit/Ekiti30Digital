#!/usr/bin/env python3
"""
kb_chunk.py: split verified, ingestible KB documents into retrievable chunks.

Reads 13_Knowledge_Base/kb_manifest.csv (from kb_validate.py) and, for every
row with ingestible == "yes", reads the document, pulls the Facts and Summary
sections, and writes one chunk per fact (plus one summary chunk) with the
source metadata a retriever and Ask Ekiti need at answer time.

Chunking rule (spec A9.3, "cite every factual claim"): one fact = one chunk,
so a retrieved chunk never mixes two claims under one citation.

Output: 13_Knowledge_Base/kb_chunks.jsonl (one JSON object per line) and
kb_chunks.csv (same data, for spreadsheet review). Deliberately no vector
store or embedding call here: this only depends on kb_manifest.csv and the
verified documents, so it can run before the embeddings/pgvector decision is
made. Embedding is a separate step that reads this file's "text" field.

Usage:
    python 13_Knowledge_Base/tools/kb_chunk.py
    python 13_Knowledge_Base/tools/kb_chunk.py --selftest
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile

MANIFEST_COLUMNS = None  # read from the CSV header, not assumed
CHUNK_FIELDS = ["chunk_id", "doc_id", "chunk_type", "text", "source_ids", "source_titles",
                 "category", "doc_type", "tier", "language", "last_verified", "path", "seq"]


def read_manifest(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_body_sections(text):
    """Return (summary_text, [fact_lines]) from a KB document's Markdown body."""
    lines = text.splitlines()
    # drop front matter if present
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            lines = lines[end + 1:]
    sections, current = {}, None
    for ln in lines:
        m = re.match(r"^##\s+(.*)$", ln)
        if m:
            current = m.group(1).strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(ln)
    summary = " ".join(x.strip() for x in sections.get("Summary", []) if x.strip())
    facts = []
    for ln in sections.get("Facts", []):
        ln = ln.strip()
        if ln.startswith("- "):
            facts.append(ln[2:].strip())
    return summary, facts


def strip_inline_citation_markers(s):
    # facts end with " [S1]" or " [S1, S2]" pointing into the document's own
    # Sources list; keep the plain claim text as the chunk, drop the marker
    return re.sub(r"\s*\[S[\w,\s]+\]\s*$", "", s).strip()


def make_id(doc_id, seq):
    return f"{doc_id}#{seq:03d}"


def build_chunks(manifest_rows, root):
    chunks, skipped, errors = [], [], []
    for row in manifest_rows:
        if row.get("ingestible") != "yes":
            skipped.append((row.get("path", ""), row.get("reason", "not ingestible")))
            continue
        full = os.path.join(root, row["path"])
        if not os.path.exists(full):
            errors.append(f"{row['path']}: file listed in manifest but not found on disk")
            continue
        with open(full, encoding="utf-8") as f:
            text = f.read()
        summary, facts = parse_body_sections(text)
        sids = [s for s in (row.get("source_ids") or "").split(";") if s]
        meta = dict(doc_id=row["id"], source_ids=";".join(sids), source_titles="",
                    category=row.get("category", ""), doc_type=row.get("doc_type", ""),
                    tier=row.get("source_tier", ""), language=row.get("language", "en"),
                    last_verified=row.get("last_verified", ""), path=row["path"])
        seq = 0
        if summary:
            seq += 1
            chunks.append(dict(chunk_id=make_id(row["id"], seq), chunk_type="summary",
                                text=summary, seq=seq, **meta))
        if not facts:
            errors.append(f"{row['path']}: verified and ingestible but has no '## Facts' bullet lines")
        for fact in facts:
            clean = strip_inline_citation_markers(fact)
            if not clean:
                continue
            seq += 1
            chunks.append(dict(chunk_id=make_id(row["id"], seq), chunk_type="fact",
                                text=clean, seq=seq, **meta))
        if seq == 0:
            errors.append(f"{row['path']}: produced zero chunks (empty Summary and Facts)")
    return chunks, skipped, errors


def write_outputs(chunks, jsonl_path, csv_path):
    os.makedirs(os.path.dirname(os.path.abspath(jsonl_path)), exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({k: c.get(k, "") for k in CHUNK_FIELDS}, ensure_ascii=False) + "\n")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHUNK_FIELDS)
        w.writeheader()
        for c in chunks:
            w.writerow({k: c.get(k, "") for k in CHUNK_FIELDS})


def run(root, manifest_path, jsonl_path, csv_path, quiet=False):
    rows = read_manifest(manifest_path)
    chunks, skipped, errors = build_chunks(rows, root)
    write_outputs(chunks, jsonl_path, csv_path)
    if not quiet:
        for path, reason in skipped:
            print(f"SKIP  {path}: {reason}")
        for e in errors:
            print(f"ERROR {e}")
        by_doc = len({c["doc_id"] for c in chunks})
        print(f"\nChunks written: {len(chunks)} from {by_doc} document(s) "
              f"| skipped: {len(skipped)} | errors: {len(errors)}")
        print(f"Wrote: {jsonl_path}\nWrote: {csv_path}")
    return chunks, skipped, errors


def selftest():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "01_History"))
    doc = """---
id: history-example
---

## Summary
Example state was formed on a date, according to one source.

## Facts
- Fact one happened on 1 October. [S1]
- Fact two also happened, per two sources. [S1, S2]

## Sources
- [S1] ...
"""
    open(os.path.join(tmp, "01_History", "example.md"), "w", encoding="utf-8").write(doc)
    doc2 = """---
id: history-empty
---

## Summary


## Facts

## Sources
"""
    open(os.path.join(tmp, "01_History", "empty.md"), "w", encoding="utf-8").write(doc2)
    manifest = os.path.join(tmp, "kb_manifest.csv")
    with open(manifest, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "path", "category", "doc_type", "status", "source_tier", "source_ids",
                    "publication_date", "last_verified", "verified_by", "language",
                    "translation_of", "period_covered", "file_sha256", "ingestible", "reason"])
        w.writerow(["history-example", "01_History/example.md", "history", "event", "verified", "A",
                    "SRC-001", "2021-10-01", "2026-09-21", "Victor", "en", "", "1996", "x", "yes", ""])
        w.writerow(["history-draft", "01_History/example.md", "history", "event", "draft", "A",
                    "SRC-001", "2021-10-01", "", "", "en", "", "1996", "x", "no", "status is draft"])
        w.writerow(["history-empty", "01_History/empty.md", "history", "event", "verified", "A",
                    "SRC-001", "2021-10-01", "2026-09-21", "Victor", "en", "", "1996", "x", "yes", ""])
        w.writerow(["history-missing", "01_History/missing.md", "history", "event", "verified", "A",
                    "SRC-001", "2021-10-01", "2026-09-21", "Victor", "en", "", "1996", "x", "yes", ""])
    chunks, skipped, errors = run(tmp, manifest, os.path.join(tmp, "c.jsonl"),
                                   os.path.join(tmp, "c.csv"), quiet=True)
    failures = []
    ex = [c for c in chunks if c["doc_id"] == "history-example"]
    if len(ex) != 3:
        failures.append(f"expected 3 chunks for history-example (1 summary + 2 facts), got {len(ex)}")
    if ex and ex[0]["chunk_type"] != "summary":
        failures.append("first chunk should be the summary")
    if any("[S1]" in c["text"] or "[S1, S2]" in c["text"] for c in ex):
        failures.append("citation markers should be stripped from chunk text")
    if len(skipped) != 1 or skipped[0][0] != "01_History/example.md":
        failures.append(f"expected history-draft to be skipped as not ingestible, got: {skipped}")
    if not any("no '## Facts'" in e for e in errors):
        failures.append("empty document should raise a 'no Facts' error")
    if not any("not found on disk" in e for e in errors):
        failures.append("missing file should raise a 'not found' error")
    ids = [c["chunk_id"] for c in ex]
    if ids != sorted(set(ids), key=ids.index) or len(set(ids)) != len(ids):
        failures.append("chunk_ids should be unique and sequential")
    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print(f"SELFTEST PASSED ({len(ex)} chunks from the example document, "
          f"{len(skipped)} skipped, {len(errors)} expected errors)")
    return 0


def main():
    global CHUNK_FIELDS
    ap = argparse.ArgumentParser(description="Chunk verified, ingestible Ask Ekiti KB documents.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--manifest", default=None,
                    help="default: 13_Knowledge_Base/kb_manifest.csv")
    ap.add_argument("--out-jsonl", default=None, help="default: 13_Knowledge_Base/kb_chunks.jsonl")
    ap.add_argument("--out-csv", default=None, help="default: 13_Knowledge_Base/kb_chunks.csv")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    manifest = a.manifest or os.path.join(a.root, "13_Knowledge_Base", "kb_manifest.csv")
    jsonl = a.out_jsonl or os.path.join(a.root, "13_Knowledge_Base", "kb_chunks.jsonl")
    csv_out = a.out_csv or os.path.join(a.root, "13_Knowledge_Base", "kb_chunks.csv")
    if not os.path.exists(manifest):
        sys.exit(f"manifest not found: {manifest} (run kb_validate.py first)")
    _, _, errors = run(a.root, manifest, jsonl, csv_out)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
