# VoltMize IR Presentation — Easy Explanation and Speaker Guide

## 1. The whole idea in one minute

VoltMize watches electricity meters in factories. It detects unusual energy use and helps a user understand the possible cause and action. During real use, people may need to find an older incident similar to the current problem.

Our retrieval question is:

> When a factory user writes an energy problem, which past incident or diagnostic record should appear first?

We created two small, fictional datasets based on the VoltMize workflow. We did **not** run or change the FYP application.

1. Unstructured incident reports are ordinary technician notes.
2. Structured diagnostic records have fields such as equipment, symptoms, meter context, cause, and action.

We applied every retrieval model taught for these data shapes, ran five queries on each dataset, and compared the ranked results using standard metrics.

## 2. What the different IR models mean

### Boolean Retrieval — unstructured text

Think of switches. For every query word, a document either contains it or does not. `AND` means all required switches must be on. `OR` means at least one can be on.

Why it suits text: word presence is easy to check.

Main weakness: basic Boolean retrieval gives a selected set, not a meaningful best-to-worst ranking. In our OR experiment, many weak matches enter the result.

Our implementation: tokenize the query and each incident report, select any report sharing at least one query word, and give every selected report the same score.

### Vector Space Model — unstructured text

Imagine each document as an arrow made from word weights. TF‑IDF makes an important, rare word heavier than a common word. Cosine similarity checks how closely the query arrow points toward a document arrow.

Why it suits text: natural-language queries can partially match a document and still receive a useful score.

Our implementation: calculate TF‑IDF for query and report terms, calculate cosine similarity, and sort from highest similarity to lowest.

### Binary Independence Model (BIM) — unstructured text

BIM treats every query word as yes/no evidence. A rare word is stronger evidence than a common word. If a report contains several strong query words, its probability-style score increases.

Why it suits text: it ranks partial matches while keeping the representation simple.

Our implementation: use Robertson/Sparck Jones rarity weights and add the weights of query terms present in each report. Repeated occurrences do not add extra evidence.

### BM25 — unstructured text

BM25 is a practical improvement over binary probabilistic ranking. It asks three questions:

1. Is the query word rare and therefore useful?
2. How often does it appear in this document?
3. Is the document long only because it contains many extra words?

Why it suits technician notes: reports have different lengths and may repeat the important fault term.

Our implementation: standard Okapi BM25 with `k1 = 1.5` and `b = 0.75`.

### Overlapped Lists — structured text

The record is divided into regions such as symptoms, cause, and action. This model rewards query words that occur together inside the same region.

Why it suits structured text: terms together in one field may express one precise concept.

Our implementation: count query matches in each field and use the best field score.

### Non‑Overlapped Lists — structured text

This model lets query evidence come from different fields. For example, `compressor` can match equipment, `night` can match meter context, and `valve` can match probable cause.

Why it suits VoltMize: a diagnosis is naturally distributed across equipment, symptoms, context, cause, and action.

Our implementation: combine unique query-term matches across all six fields and rank by query coverage.

### Proximal Nodes — structured text

Treat the fields as nodes in a structure. A document scores higher when matching nodes are close to one another.

Why it suits structured text: closeness can indicate that terms belong to the same local explanation.

Our implementation: find the field positions containing query terms, reward coverage, then add a larger bonus for smaller field distance.

## 3. The datasets and why they are connected to the FYP

### Unstructured dataset

File: `unstructured_text/dataset/incident_reports.json`

It contains 15 fictional reports about:

- compressor energy waste;
- low motor power factor;
- weekend idle consumption;
- chiller and temperature behavior;
- meter communication gaps;
- conveyor bearing wear;
- voltage imbalance;
- peak demand and other factory events.

These are relevant because VoltMize turns meter readings into anomaly episodes and operational explanations. A technician note is a realistic record that a user may want to retrieve later.

### Structured dataset

File: `structured_text/dataset/diagnostic_records.json`

It contains 12 records. Every record has:

- `equipment`;
- `summary`;
- `symptoms`;
- `meter_context`;
- `probable_cause`;
- `action`.

These fields mirror the FYP workflow: identify equipment, observe abnormal signals, add context, infer a cause, and recommend an action.

### Queries and ground truth

Each dataset has a `queries.json`. Every query contains a manually defined `relevant` list. That list is the answer key used by the evaluation code.

Examples:

- `compressor abnormal high energy night shift`
- `low power factor motor reactive energy`
- `weekend no production shutdown consumption`
- `temperature chiller excess energy cause`
- `missing meter readings communication action`

## 4. How to explain the KPIs

- **Precision@3:** Out of the first three results, how many are actually relevant?
- **Recall@3:** Out of all relevant records, how many did we find in the first three?
- **F1@3:** One balanced number combining precision and recall.
- **MRR:** How early did the first relevant result appear? Rank 1 gives 1.0; rank 2 gives 0.5.
- **nDCG@3:** Did we put the relevant results near the top, where users will see them first?

The most useful main KPI for this presentation is nDCG@3 because the assignment is about ranked retrieval.

## 5. Actual measured result

| Data type | Model | Precision@3 | Recall@3 | MRR | nDCG@3 |
|---|---|---:|---:|---:|---:|
| Unstructured | Boolean | 0.267 | 0.467 | 0.640 | 0.449 |
| Unstructured | Vector Space | 0.600 | 0.900 | 1.000 | 0.923 |
| Unstructured | BIM | 0.600 | 0.900 | 1.000 | 0.923 |
| Unstructured | BM25 | 0.600 | 0.900 | 1.000 | 0.923 |
| Structured | Overlapped Lists | 0.400 | 0.800 | 1.000 | 0.845 |
| Structured | Non‑Overlapped Lists | **0.533** | **1.000** | **1.000** | **0.968** |
| Structured | Proximal Nodes | 0.467 | 0.900 | 1.000 | 0.907 |

Honest conclusion:

- The three ranked unstructured models tie on this small binary benchmark. We choose BM25 as the practical baseline because its frequency saturation and length normalization make it more robust when the collection grows.
- Non‑Overlapped Lists is the measured structured winner. It fits the FYP because diagnostic evidence is spread across several fields.
- We should not claim that 0.968 versus 0.923 proves one model is universally better; those scores come from different datasets.

## 6. How to present the slides effectively

Do not read every bullet. Use the same four-question pattern for each model:

1. **What goes in?** A query and a dataset.
2. **What happens inside?** Explain the scoring idea in one sentence.
3. **What comes out?** A selected set or ranked list.
4. **Why did that result come first?** Point at its matching evidence.

### Suggested speaker flow

- **Slides 1–3:** Explain the FYP problem and define query, document, and result.
- **Slides 4–5:** Show that model choice depends on data type and explain the KPIs.
- **Slide 6:** Read only the U01 example. State that all 15 reports are synthetic but FYP-relevant.
- **Slides 7–10:** Follow the visual path from query to matching evidence, calculation, score, and top-three ranking. Give about 40 seconds per model.
- **Slide 11:** Show the real BM25 implementation. Point to tokenization, document length, the highlighted scoring lines, and final sorting.
- **Slide 12:** Say the important result: ranking greatly beats unranked Boolean retrieval. Be open about the three-way tie.
- **Slide 13:** Walk through the six structured fields once.
- **Slides 14–16:** Contrast “best single field,” “union across fields,” and “nearby nodes.”
- **Slide 17:** Explain why distributed evidence made Non‑Overlapped Lists win.
- **Slide 18:** State the final model decision for each data type.
- **Slide 19:** Explain how model assumptions create strengths and weaknesses.
- **Slide 20:** Keep the additional query bank as an appendix.
- **Slide 21:** Finish with the two recommendations, not with metric details.

### Good final wording

> We did not attach IR code to the production FYP. We used the FYP workflow to create two realistic evidence collections. On free-text reports, ranked models were much better than Boolean OR, and BM25 is our recommended baseline. On structured diagnostic records, Non‑Overlapped Lists performed best because the useful evidence was spread across fields. This shows that retrieval quality depends on matching the model’s assumptions to the shape of the data.

## 7. Questions the instructor may ask

**Why is Boolean weak here?**  
Our OR query admits any report sharing one term, and basic Boolean retrieval has no relevance ranking. It is still useful for strict filters.

**Why did VSM, BIM, and BM25 tie?**  
The dataset is small and the judgments are binary. Their numeric scores differ, but the relevant top-three ordering is often the same. A larger dataset with longer and noisier reports would separate them more clearly.

**Why choose BM25 after a tie?**  
It has useful behavior not exercised strongly by this tiny benchmark: term-frequency saturation and document-length normalization. We call it a practical selection, not a statistically proven win.

**Why did Non‑Overlapped Lists win?**  
The query mixes several kinds of evidence, and those words appear in different JSON fields. The model is designed to combine those independent regions.

**Is the dataset real?**  
No. It is deterministic synthetic course data based on the FYP workflow. This avoids exposing or depending on production data while keeping the retrieval task relevant.

**Did you run the FYP?**  
No. The demo is isolated and only uses the repository documentation and data concepts to understand the domain.
