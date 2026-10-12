"""Proximal Nodes: reward matching structural regions that are close together."""
from pathlib import Path
import itertools
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from common import evaluate, load_json, print_result, save_result, tokenize

documents = load_json(ROOT / "structured_text/dataset/diagnostic_records.json")
queries = load_json(ROOT / "structured_text/dataset/queries.json")
FIELDS = ["equipment", "summary", "symptoms", "meter_context", "probable_cause", "action"]
nodes = {d["id"]: [set(tokenize(d[field])) for field in FIELDS] for d in documents}


def search(query: str):
    query_terms = set(tokenize(query))
    scored = []
    for doc_id, regions in nodes.items():
        locations = {term: [i for i, terms in enumerate(regions) if term in terms] for term in query_terms}
        present = [term for term, positions in locations.items() if positions]
        coverage = len(present) / len(query_terms)
        closeness = 0.0
        for left, right in itertools.combinations(present, 2):
            distance = min(abs(a - b) for a in locations[left] for b in locations[right])
            closeness += 1 / (1 + distance)
        score = 2 * coverage + closeness
        if score > 0:
            scored.append((doc_id, score))
    return sorted(scored, key=lambda item: (-item[1], item[0]))


if __name__ == "__main__":
    result = evaluate("Proximal Nodes", queries, search)
    save_result(result, HERE / "results.json")
    print_result(result)
