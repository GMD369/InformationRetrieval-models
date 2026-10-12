"""Binary Independence Model: score query-term presence with RSJ weights."""
from collections import Counter
from pathlib import Path
import math
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from common import evaluate, load_json, print_result, save_result, tokenize

documents = load_json(ROOT / "unstructured_text/dataset/incident_reports.json")
queries = load_json(ROOT / "unstructured_text/dataset/queries.json")
terms_by_doc = {d["id"]: set(tokenize(d["title"] + " " + d["text"])) for d in documents}
N = len(documents)
df = Counter(term for terms in terms_by_doc.values() for term in terms)


def search(query: str):
    query_terms = set(tokenize(query))
    scored = []
    for doc_id, terms in terms_by_doc.items():
        # Robertson/Sparck Jones weight without relevance feedback.
        score = sum(math.log((N - df[term] + 0.5) / (df[term] + 0.5)) for term in query_terms if term in terms)
        if score > 0:
            scored.append((doc_id, score))
    return sorted(scored, key=lambda item: (-item[1], item[0]))


if __name__ == "__main__":
    result = evaluate("Binary Independence Model", queries, search)
    save_result(result, HERE / "results.json")
    print_result(result)
