"""Okapi BM25 with k1=1.5 and b=0.75."""
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
doc_tf = {d["id"]: Counter(tokenize(d["title"] + " " + d["text"])) for d in documents}
N = len(documents)
df = Counter(term for counts in doc_tf.values() for term in counts)
avgdl = sum(sum(counts.values()) for counts in doc_tf.values()) / N
k1, b = 1.5, 0.75


def search(query: str):
    query_terms = tokenize(query)
    scored = []
    for doc_id, counts in doc_tf.items():
        dl = sum(counts.values())
        score = 0.0
        for term in query_terms:
            tf = counts[term]
            if not tf:
                continue
            idf = math.log(1 + (N - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
        if score > 0:
            scored.append((doc_id, score))
    return sorted(scored, key=lambda item: (-item[1], item[0]))


if __name__ == "__main__":
    result = evaluate("BM25", queries, search)
    save_result(result, HERE / "results.json")
    print_result(result)
