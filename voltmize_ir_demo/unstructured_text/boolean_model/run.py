"""Boolean retrieval: include documents matching any query term (OR)."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from common import evaluate, load_json, print_result, save_result, tokenize

documents = load_json(ROOT / "unstructured_text/dataset/incident_reports.json")
queries = load_json(ROOT / "unstructured_text/dataset/queries.json")
document_terms = {doc["id"]: set(tokenize(doc["title"] + " " + doc["text"])) for doc in documents}


def search(query: str):
    terms = set(tokenize(query))
    # Classical Boolean retrieval selects a set, not a true ranking. Document ID
    # order is used only so that the output is deterministic.
    return [(doc_id, 1.0) for doc_id in sorted(document_terms) if document_terms[doc_id] & terms]


if __name__ == "__main__":
    result = evaluate("Boolean OR (unranked)", queries, search)
    save_result(result, HERE / "results.json")
    print_result(result)
