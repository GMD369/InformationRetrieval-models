# VoltMize Information Retrieval Demo

This is a self-contained course demonstration. It uses the workflow and vocabulary of the VoltMize FYP, but it does **not** import, start, modify, or depend on the production FYP code.

## What is included

- **Unstructured text dataset:** 15 fictional technician incident reports.
- **Structured text dataset:** 12 fictional diagnostic JSON records.
- **Five judged queries per dataset:** each query includes its relevant document IDs.
- **Seven IR models:** Boolean, Vector Space, BIM, BM25, Overlapped Lists, Non-Overlapped Lists, and Proximal Nodes.
- **Evaluation:** Precision@3, Recall@3, F1@3, MRR, and nDCG@3.
- **Evidence:** JSON results, plain console captures, PNG query-output captures, CSV comparison, and charts.
- **Presentation:** `presentation/VoltMize_IR_Presentation.pptx`.
- **Speaking guide:** `PRESENTATION_GUIDE.md`.

## Folder organization

```text
voltmize_ir_demo/
├── unstructured_text/
│   ├── dataset/
│   ├── boolean_model/
│   ├── vector_space/
│   ├── bim/
│   └── bm25/
├── structured_text/
│   ├── dataset/
│   ├── overlapped_lists/
│   ├── non_overlapped_lists/
│   └── proximal_nodes/
├── artifacts/
├── presentation/
├── generate_datasets.py
├── run_all.py
├── build_artifacts.py
├── build_presentation.py
└── build_all.py
```

Every model folder contains:

- `run.py` — simple implementation;
- `results.json` — machine-readable query results and metrics;
- `console_output.txt` — the actual printed run.

## Run it

From this directory:

```powershell
python build_all.py
```

Or inspect a single model:

```powershell
python unstructured_text\bm25\run.py
python structured_text\non_overlapped_lists\run.py
```

The runs are deterministic. No network, database, or FYP service is required.

## Honest interpretation

This is a small classroom benchmark using synthetic records. It is useful for explaining and comparing retrieval behavior, but its scores are not evidence of production performance. VSM, BIM, and BM25 tie on the chosen unstructured binary judgments. BM25 is selected as the practical free-text baseline because it additionally handles repeated terms and document length. Non-Overlapped Lists is the measured winner on the structured set.
