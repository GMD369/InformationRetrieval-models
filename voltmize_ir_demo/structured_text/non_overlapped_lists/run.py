"""Non-Overlapped Lists: retrieve terms independently across all regions."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from common import evaluate, load_json, print_result, save_result, tokenize

documents = load_json(ROOT / "structured_text/dataset/diagnostic_records.json")
queries = load_json(ROOT / "structured_text/dataset/queries.json")
FIELDS = ["equipment", "summary", "symptoms", "meter_context", "probable_cause", "action"]
all_terms = {d["id"]: set(tokenize(" ".join(d[field] for field in FIELDS))) for d in documents}


def search(query: str):
    query_terms = set(tokenize(query))
    scored = [(doc_id, len(query_terms & terms) / len(query_terms)) for doc_id, terms in all_terms.items()]
    return sorted((item for item in scored if item[1] > 0), key=lambda item: (-item[1], item[0]))


if __name__ == "__main__":
    result = evaluate("Non-Overlapped Lists", queries, search)
    save_result(result, HERE / "results.json")
    print_result(result)
