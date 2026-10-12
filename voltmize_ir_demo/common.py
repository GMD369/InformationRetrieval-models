from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path


STOP = {"a", "an", "and", "are", "as", "at", "be", "because", "by", "during", "for", "from", "had", "in", "is", "it", "near", "of", "on", "or", "so", "the", "to", "was", "were", "with"}


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower().replace("off-hours", "off hours"))
    normalized = []
    for token in tokens:
        if token in STOP:
            continue
        if token.endswith("ings") and len(token) > 6:
            token = token[:-1]
        elif token.endswith("ed") and len(token) > 5:
            token = token[:-2]
        elif token.endswith("s") and len(token) > 4:
            token = token[:-1]
        normalized.append(token)
    return normalized


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def metrics(ranked: list[str], relevant: list[str], k: int = 3) -> dict[str, float]:
    rel = set(relevant)
    top = ranked[:k]
    hits = sum(doc_id in rel for doc_id in top)
    precision = hits / k
    recall = hits / len(rel) if rel else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    reciprocal_rank = next((1 / (i + 1) for i, doc_id in enumerate(ranked) if doc_id in rel), 0.0)
    dcg = sum((1.0 if doc_id in rel else 0.0) / math.log2(i + 2) for i, doc_id in enumerate(top))
    ideal_hits = min(len(rel), k)
    idcg = sum(1 / math.log2(i + 2) for i in range(ideal_hits))
    ndcg = dcg / idcg if idcg else 0.0
    return {"precision@3": precision, "recall@3": recall, "f1@3": f1, "mrr": reciprocal_rank, "ndcg@3": ndcg}


def evaluate(model_name: str, queries: list[dict], search) -> dict:
    query_results = []
    for query in queries:
        ranked_pairs = search(query["text"])
        ranked = [doc_id for doc_id, _ in ranked_pairs]
        item_metrics = metrics(ranked, query["relevant"])
        query_results.append({
            "query_id": query["id"],
            "query": query["text"],
            "relevant": query["relevant"],
            "top_results": [{"rank": i + 1, "document": doc_id, "score": round(float(score), 4)} for i, (doc_id, score) in enumerate(ranked_pairs[:3])],
            "metrics": {key: round(value, 4) for key, value in item_metrics.items()},
        })
    aggregate = {key: round(sum(item["metrics"][key] for item in query_results) / len(query_results), 4) for key in query_results[0]["metrics"]}
    return {"model": model_name, "query_count": len(queries), "aggregate": aggregate, "queries": query_results}


def save_result(result: dict, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")


def print_result(result: dict) -> None:
    print(f"MODEL: {result['model']}")
    print("=" * 72)
    for item in result["queries"]:
        print(f"{item['query_id']} | QUERY: {item['query']}")
        print(f"EXPECTED RELEVANT: {', '.join(item['relevant'])}")
        for hit in item["top_results"]:
            print(f"  {hit['rank']}. {hit['document']}   score={hit['score']:.4f}")
        m = item["metrics"]
        print(f"  P@3={m['precision@3']:.3f}  R@3={m['recall@3']:.3f}  MRR={m['mrr']:.3f}  nDCG@3={m['ndcg@3']:.3f}")
        print()
    a = result["aggregate"]
    print("AVERAGE:", "  ".join(f"{key}={value:.3f}" for key, value in a.items()))


def term_frequencies(text: str) -> Counter:
    return Counter(tokenize(text))
