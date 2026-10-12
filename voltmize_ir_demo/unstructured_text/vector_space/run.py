"""Vector Space Model using TF-IDF weights and cosine similarity."""
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
idf = {term: math.log((N + 1) / (freq + 1)) + 1 for term, freq in df.items()}


def vector(counts):
    return {term: (1 + math.log(freq)) * idf.get(term, math.log(N + 1) + 1) for term, freq in counts.items()}


doc_vectors = {doc_id: vector(counts) for doc_id, counts in doc_tf.items()}


def cosine(left, right):
    dot = sum(weight * right.get(term, 0.0) for term, weight in left.items())
    norm_l = math.sqrt(sum(weight * weight for weight in left.values()))
    norm_r = math.sqrt(sum(weight * weight for weight in right.values()))
    return dot / (norm_l * norm_r) if norm_l and norm_r else 0.0


def search(query: str):
    query_vector = vector(Counter(tokenize(query)))
    scored = [(doc_id, cosine(query_vector, doc_vector)) for doc_id, doc_vector in doc_vectors.items()]
    return sorted((item for item in scored if item[1] > 0), key=lambda item: (-item[1], item[0]))


if __name__ == "__main__":
    result = evaluate("Vector Space (TF-IDF cosine)", queries, search)
    save_result(result, HERE / "results.json")
    print_result(result)
