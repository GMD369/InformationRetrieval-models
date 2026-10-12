# Learning the IR Models Used in This Project

This document explains the models independently of VoltMize. First understand how each model works on unstructured and structured datasets; the FYP connection can be studied afterward.

## Where the raw results are stored

Each model folder contains two raw result files:

- `results.json`: machine-readable results, scores, relevant-document IDs, and evaluation metrics for every query.
- `console_output.txt`: the exact text printed when the model was run.

### Unstructured-model results

- Boolean: `unstructured_text/boolean_model/results.json`
- Vector Space: `unstructured_text/vector_space/results.json`
- BIM: `unstructured_text/bim/results.json`
- BM25: `unstructured_text/bm25/results.json`

### Structured-model results

- Overlapped Lists: `structured_text/overlapped_lists/results.json`
- Non-Overlapped Lists: `structured_text/non_overlapped_lists/results.json`
- Proximal Nodes: `structured_text/proximal_nodes/results.json`

The combined comparison is stored in:

```text
artifacts/model_comparison.csv
```

Query-result screenshots and charts are stored in:

```text
artifacts/
```

Run every model again with:

```powershell
python run_all.py
```

This regenerates every `results.json` and `console_output.txt` file.

---

# Part 1 — Unstructured-text retrieval

## Dataset

The unstructured dataset is:

```text
unstructured_text/dataset/incident_reports.json
```

It contains 15 ordinary text documents. Each document has an ID, title, and free-text paragraph:

```json
{
  "id": "U01",
  "title": "Compressor-1 night shift anomaly",
  "text": "During the night shift Compressor-1 drew unusually high energy..."
}
```

The queries and relevance judgments are in:

```text
unstructured_text/dataset/queries.json
```

A relevance judgment is the answer key showing which documents should be considered relevant for a query.

## Example query used for all unstructured models

```text
compressor abnormal high energy night shift
```

After preprocessing, the query terms are:

```text
compressor, abnormal, high, energy, night, shift
```

The manually judged relevant documents are:

```text
U01, U06, U11
```

## Query-term matches in the documents

| Document | Matching query terms | Term frequencies |
|---|---|---|
| U01 | compressor, energy, high, night, shift | compressor ×2, night ×2, shift ×2 |
| U02 | shift | shift ×1 |
| U03 | shift | shift ×1 |
| U04 | energy, high | each ×1 |
| U05 | energy | ×1 |
| U06 | abnormal, compressor, shift | each ×1 |
| U07 | energy | ×1 |
| U09 | energy, high | each ×1 |
| U10 | energy | ×1 |
| U11 | compressor, night | compressor ×2, night ×1 |
| U12 | energy, high | each ×1 |
| U14 | energy | ×1 |

The models see these same matches but score them differently.

---

## 1. Boolean Retrieval

Implementation:

```text
unstructured_text/boolean_model/run.py
```

### How it works

Boolean retrieval checks whether terms are present or absent. It commonly supports:

- `AND`: every required term must occur.
- `OR`: at least one term must occur.
- `NOT`: the specified term must not occur.

This implementation uses OR:

```text
compressor OR abnormal OR high OR energy OR night OR shift
```

A document is selected if it contains at least one term. Every selected document gets the same score:

```text
score = 1
```

Basic Boolean retrieval selects a set; it does not naturally rank that set. Documents with equal scores are displayed by document ID so the output is deterministic.

### Result

```text
1. U01   score = 1.0000   relevant
2. U02   score = 1.0000   not relevant
3. U03   score = 1.0000   not relevant
```

U02 and U03 appear because they contain `shift`. Boolean OR cannot recognize that U01 matches five terms while they match only one.

### Pros

- Easy to understand and implement.
- Fast for exact filtering.
- Predictable behavior.
- Useful when strict conditions are known.
- Supports AND, OR, and NOT.

### Cons

- Basic Boolean retrieval has no relevance ranking.
- OR can retrieve many irrelevant documents.
- AND can be too strict and return nothing.
- One matching term may be treated like several matching terms.
- It ignores term rarity and frequency.

---

## 2. Vector Space Model

Implementation:

```text
unstructured_text/vector_space/run.py
```

### How it works

The Vector Space Model converts the query and every document into numerical vectors using TF-IDF.

### Term Frequency — TF

TF is how often a word occurs in a document. In U01:

```text
compressor = 2
night      = 2
shift      = 2
high       = 1
energy     = 1
abnormal   = 0
```

### Inverse Document Frequency — IDF

IDF gives more importance to rare words. A common word such as `energy` carries less information than a rarer word such as `compressor` or `abnormal`.

### Cosine similarity

The model compares the direction of the query vector with each document vector:

```text
larger cosine similarity = more similar term-weight pattern
```

### Result

```text
1. U01   score = 0.4365   relevant
2. U06   score = 0.2413   relevant
3. U11   score = 0.2093   relevant
```

U01 ranks first because it covers five query terms and repeats important terms. U06 contains the rare word `abnormal`, so its smaller set of matches still provides strong evidence.

### Pros

- Produces ranked results.
- Supports partial matching.
- Rare terms receive more weight.
- Repeated terms can increase relevance.
- Cosine similarity reduces the effect of raw document size.

### Cons

- Does not understand meaning or synonyms.
- Mostly ignores word order.
- Separate matching words can score well even when their combined meaning is wrong.
- TF-IDF weights change when the collection changes.

---

## 3. Binary Independence Model — BIM

Implementation:

```text
unstructured_text/bim/run.py
```

### How it works

BIM treats each query term as binary evidence:

```text
present = 1
absent  = 0
```

It gives rare terms more weight using a Robertson/Sparck Jones-style weight:

```text
weight(term) = log((N - df + 0.5) / (df + 0.5))
```

Where:

- `N` is the total number of documents.
- `df` is the number of documents containing the term.

The score is the sum of the weights of query terms present in the document.

Unlike the Vector Space Model, BIM does not care how many times a word occurs. A term appearing once and the same term appearing five times provide the same binary evidence.

### Result

```text
1. U01   score = 4.7107   relevant
2. U06   score = 4.4799   relevant
3. U11   score = 2.9594   relevant
```

U06 scores strongly because `abnormal` is rare, even though it matches fewer total terms than U01.

### Pros

- Produces ranked results.
- Has a simple probabilistic interpretation.
- Rare terms provide stronger evidence.
- Improves on unranked Boolean selection.
- Does not need term-frequency processing.

### Cons

- Ignores repeated occurrences.
- Assumes query terms provide independent evidence.
- Ignores word order and phrases.
- Does not understand synonyms or semantics.
- Is less flexible than BM25 for ordinary text ranking.

---

## 4. BM25

Implementation:

```text
unstructured_text/bm25/run.py
```

### How it works

BM25 combines three ideas:

1. **Term rarity:** rare query terms contribute more.
2. **Term frequency:** repeated query terms increase a document's score.
3. **Length normalization:** long documents do not win simply because they contain more words.

BM25 uses frequency saturation. The second occurrence of a term helps, but repeating the same word many times eventually adds very little value.

This implementation uses:

```text
k1 = 1.5
b  = 0.75
```

The simplified idea is:

```text
BM25 score = rarity × controlled frequency × length normalization
```

### Result

```text
1. U01   score = 7.9923   relevant
2. U06   score = 5.2178   relevant
3. U11   score = 4.0005   relevant
```

U01 ranks first because it matches five terms, repeats several important terms, and has a reasonable document length.

### Pros

- Strong general-purpose text-ranking baseline.
- Uses term rarity and frequency.
- Prevents unlimited reward for repeated words.
- Normalizes different document lengths.
- Normally works well without training a machine-learning model.

### Cons

- Does not understand meaning or synonyms.
- Mostly ignores word order.
- Parameters may require tuning.
- Does not directly use field structure unless extended.

## Unstructured-model summary

| Model | Main criterion | U01 score |
|---|---|---:|
| Boolean | At least one query term is present | 1.0000 |
| Vector Space | TF-IDF cosine similarity | 0.4365 |
| BIM | Weighted binary term evidence | 4.7107 |
| BM25 | Rarity, frequency, and document length | 7.9923 |

The numerical scores cannot be directly compared across models because each model uses a different scoring scale. Their rankings and evaluation metrics should be compared instead.

---

# Part 2 — Structured-text retrieval

## Dataset

The structured dataset is:

```text
structured_text/dataset/diagnostic_records.json
```

It contains 12 JSON records. Every record has six regions:

```text
equipment
summary
symptoms
meter_context
probable_cause
action
```

Example:

```json
{
  "id": "S01",
  "equipment": "Compressor-1",
  "summary": "High energy during night shift",
  "symptoms": "power 94 kW; idle production; repeated cycling",
  "meter_context": "night shift; total consumption 488 kWh",
  "probable_cause": "unload valve leakage",
  "action": "inspect valve and reduce pressure setpoint"
}
```

Queries and relevance judgments are stored in:

```text
structured_text/dataset/queries.json
```

## Example query used for all structured models

```text
night shift compressor high energy cause action
```

The relevant documents are:

```text
S01, S02
```

Important implementation detail: this simple implementation searches field values, not field names. Therefore, the query words `cause` and `action` do not match merely because fields are named `probable_cause` and `action`.

## Matching regions

### S01

```text
equipment:     compressor
summary:       energy, high, night, shift
meter_context: night, shift
```

Unique matches:

```text
compressor, energy, high, night, shift
```

### S02

```text
equipment:     compressor
summary:       compressor
symptoms:      shift
meter_context: shift
```

Unique matches:

```text
compressor, shift
```

### S03

```text
symptoms:      high
meter_context: energy, shift
```

Unique matches:

```text
high, energy, shift
```

---

## 5. Overlapped Lists

Implementation:

```text
structured_text/overlapped_lists/run.py
```

### How it works

The model asks:

> In which single region do the most query terms occur together?

The implementation calculates:

```text
score = best region match count
        + best region match count / query length
```

### S01 calculation

S01's summary contains four query terms together:

```text
night, shift, high, energy
```

Therefore:

```text
score = 4 + 4/7 = 4.5714
```

### S03 calculation

Its best region contains two terms:

```text
energy, shift
```

Therefore:

```text
score = 2 + 2/7 = 2.2857
```

### Result

```text
1. S01   score = 4.5714   relevant
2. S03   score = 2.2857   not relevant
3. S06   score = 2.2857   not relevant
```

S02 is relevant but misses the top three because its matching evidence is separated across fields.

### Pros

- Rewards meaningful term co-occurrence.
- Useful for exact multi-term concepts.
- Can provide high precision.
- Preserves region boundaries.
- Easy to explain.

### Cons

- Can miss evidence distributed across fields.
- Depends heavily on field design.
- Broad fields can receive an advantage.
- Does not understand synonyms.
- May produce lower recall.

---

## 6. Non-Overlapped Lists

Implementation:

```text
structured_text/non_overlapped_lists/run.py
```

### How it works

This model asks:

> How many unique query terms occur anywhere in the record?

The terms can appear in separate regions.

```text
score = unique matched query terms / total query terms
```

### Calculations

S01 matches five unique query terms:

```text
5/7 = 0.7143
```

S03 matches three:

```text
3/7 = 0.4286
```

S02 matches two:

```text
2/7 = 0.2857
```

### Result

```text
1. S01   score = 0.7143   relevant
2. S03   score = 0.4286   not relevant
3. S02   score = 0.2857   relevant
```

S02 reaches the top three because evidence from its different fields is combined.

### Pros

- Finds evidence distributed across fields.
- Usually provides better recall.
- Has simple scoring.
- Useful for exploratory structured search.
- Works when a query combines multiple types of evidence.

### Cons

- Ignores whether terms occur together.
- Unrelated fields can accidentally combine into a high score.
- All fields currently have equal importance.
- Ignores term frequency.
- Ignores structural distance.

---

## 7. Proximal Nodes

Implementation:

```text
structured_text/proximal_nodes/run.py
```

### How it works

Fields are treated as ordered nodes:

```text
0 equipment
1 summary
2 symptoms
3 meter_context
4 probable_cause
5 action
```

The score has coverage and proximity components:

```text
score = 2 × query coverage + proximity bonuses
```

The pairwise proximity bonus is:

```text
1 / (1 + distance)
```

Examples:

```text
same node:       distance 0 → bonus 1.00
adjacent nodes:  distance 1 → bonus 0.50
two nodes apart: distance 2 → bonus 0.33
```

### S03 calculation

S03 matches:

```text
high   → symptoms
energy → meter_context
shift  → meter_context
```

Coverage contribution:

```text
2 × 3/7 = 0.8571
```

Proximity contributions:

```text
energy and shift in same node → 1.00
high and energy adjacent      → 0.50
high and shift adjacent       → 0.50
```

Final score:

```text
0.8571 + 2.00 = 2.8571
```

### Result

```text
1. S01   score = 9.4286   relevant
2. S03   score = 2.8571   not relevant
3. S06   score = 1.5714   not relevant
```

### Pros

- Uses document structure.
- Rewards terms in the same or nearby regions.
- Is more expressive than simple field matching.
- Suits XML, JSON, HTML, and sectioned documents.
- Distinguishes local evidence from widely scattered evidence.

### Cons

- Assumes structural distance has meaning.
- Depends on field ordering.
- Is more complex than list-based methods.
- A poor structural design creates poor scores.
- May miss relevant documents whose evidence is far apart.

## Structured-model summary

| Model | Main question |
|---|---|
| Overlapped Lists | Do the query terms occur together in one field? |
| Non-Overlapped Lists | Do the query terms occur anywhere across the fields? |
| Proximal Nodes | Are the fields containing the terms structurally close? |

In short:

```text
Overlapped     = together
Non-Overlapped = anywhere
Proximal       = structurally close
```

---

# Evaluation Metrics

The project uses:

```text
Precision@3
Recall@3
F1@3
MRR
nDCG@3
```

The `@3` means that only the first three results are evaluated.

## Precision@3

Precision asks:

> How many of the first three results are relevant?

```text
Precision@3 = relevant results in top 3 / 3
```

Example:

```text
1. S01 relevant
2. S03 not relevant
3. S02 relevant
```

Therefore:

```text
Precision@3 = 2/3 = 0.667
```

High precision means the user sees less irrelevant material.

## Recall@3

Recall asks:

> How many of all relevant documents were found in the first three?

```text
Recall@3 = relevant results found in top 3 / total relevant documents
```

If S01 and S02 are the only relevant documents and both are retrieved:

```text
Recall@3 = 2/2 = 1.000
```

High recall means fewer relevant documents were missed.

## Precision versus recall

Suppose 10 documents are relevant, but the system retrieves only three and all three are relevant:

```text
Precision@3 = 3/3  = 1.0
Recall@3    = 3/10 = 0.3
```

The results are clean, but most relevant documents were not recovered.

## F1@3

F1 balances precision and recall:

```text
F1 = 2 × Precision × Recall / (Precision + Recall)
```

For precision `0.667` and recall `1.000`:

```text
F1 ≈ 0.800
```

F1 is high only when precision and recall are both reasonably high.

## MRR — Mean Reciprocal Rank

MRR measures how early the first relevant result appears.

For one query:

```text
Reciprocal Rank = 1 / rank of first relevant result
```

Examples:

```text
first relevant at rank 1 → 1.000
first relevant at rank 2 → 0.500
first relevant at rank 3 → 0.333
no relevant result       → 0
```

MRR is the average reciprocal rank over all queries. It only considers the first relevant result.

## nDCG@3

nDCG means Normalized Discounted Cumulative Gain. It measures whether relevant documents appear near the top.

Documents at lower ranks receive a smaller reward:

```text
rank 1 → largest reward
rank 2 → smaller reward
rank 3 → still smaller reward
```

The actual ranking quality is divided by the best possible ranking quality:

```text
nDCG@3 = actual DCG / ideal DCG
```

Its range is:

```text
0 = poor ranking
1 = ideal ranking
```

Example of an ideal top-three ranking:

```text
1. relevant
2. relevant
3. not relevant
```

Example of a weaker ranking:

```text
1. not relevant
2. not relevant
3. relevant
```

Both rankings found relevant material, but nDCG correctly rewards the first one for placing relevant results earlier.

## Which metric should be used?

- Use **Precision@3** to measure how clean the first three results are.
- Use **Recall@3** to measure how much relevant material was recovered.
- Use **F1@3** when precision and recall should be balanced.
- Use **MRR** when finding one correct result quickly is most important.
- Use **nDCG@3** when the complete ordering of the first three results matters.

For this project, nDCG@3 is particularly useful because the models are being evaluated as ranking systems.

---

# Measured Overall Results

| Data type | Model | Precision@3 | Recall@3 | F1@3 | MRR | nDCG@3 |
|---|---|---:|---:|---:|---:|---:|
| Unstructured | Boolean | 0.267 | 0.467 | 0.327 | 0.640 | 0.449 |
| Unstructured | Vector Space | 0.600 | 0.900 | 0.700 | 1.000 | 0.923 |
| Unstructured | BIM | 0.600 | 0.900 | 0.700 | 1.000 | 0.923 |
| Unstructured | BM25 | 0.600 | 0.900 | 0.700 | 1.000 | 0.923 |
| Structured | Overlapped Lists | 0.400 | 0.800 | 0.520 | 1.000 | 0.845 |
| Structured | Non-Overlapped Lists | 0.533 | 1.000 | 0.680 | 1.000 | 0.968 |
| Structured | Proximal Nodes | 0.467 | 0.900 | 0.600 | 1.000 | 0.907 |

The three ranked unstructured models tie on this small dataset. BM25 remains the practical baseline because it also includes term-frequency saturation and document-length normalization. Non-Overlapped Lists gives the strongest measured result for the structured dataset because it combines evidence distributed across fields.
