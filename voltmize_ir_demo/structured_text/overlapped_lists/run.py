"""Overlapped Lists: reward query terms that occur together in one region."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from common import evaluate, load_json, print_result, save_result, tokenize

documents = load_json(ROOT / "structured_text/dataset/diagnostic_records.json")
queries = load_json(ROOT / "structured_text/dataset/queries.json")
FIELDS = ["equipment", "summary", "symptoms", "meter_context", "probable_cause", "action"]
region_terms = {d["id"]: {field: set(tokenize(d[field])) for field in FIELDS} for d in documents}


def search(query: str):
    query_terms = set(tokenize(query))
    scored = []
    for doc_id, regions in region_terms.items():
        matches = [len(query_terms & terms) for terms in regions.values()]
        best = max(matches)
        # The overlap model prefers co-occurrence inside one structural region.
        score = best + (best / len(query_terms) if query_terms else 0)
        if score > 0:
            scored.append((doc_id, score))
    return sorted(scored, key=lambda item: (-item[1], item[0]))


if __name__ == "__main__":
    result = evaluate("Overlapped Lists", queries, search)
    save_result(result, HERE / "results.json")
    print_result(result)
