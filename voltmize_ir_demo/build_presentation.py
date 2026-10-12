"""Create the editable PowerPoint presentation from measured demo artifacts."""
from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).parent
ART = ROOT / "artifacts"
OUT = ROOT / "presentation"
OUT.mkdir(exist_ok=True)

NAVY = RGBColor(7, 17, 31)
PANEL = RGBColor(14, 32, 53)
PANEL2 = RGBColor(19, 47, 76)
BLUE = RGBColor(74, 144, 245)
TEAL = RGBColor(45, 212, 191)
GREEN = RGBColor(52, 211, 153)
AMBER = RGBColor(245, 158, 11)
WHITE = RGBColor(248, 250, 252)
MUTED = RGBColor(160, 174, 192)
RED = RGBColor(248, 113, 113)


def add_bg(slide, number: int, section: str = "VOLT MIZE × INFORMATION RETRIEVAL"):
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = NAVY
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.08))
    line.fill.solid(); line.fill.fore_color.rgb = TEAL; line.line.fill.background()
    add_text(slide, section, 0.45, 0.20, 8.5, 0.28, 10, MUTED, True, letter_spacing=1.1)
    add_text(slide, f"{number:02d}", 12.25, 0.18, 0.55, 0.28, 11, MUTED, True, align=PP_ALIGN.RIGHT)


def add_text(slide, text, x, y, w, h, size=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT, font="Aptos", valign=MSO_ANCHOR.TOP, letter_spacing=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear(); tf.margin_left = tf.margin_right = 0; tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = valign; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.alignment = align
    run = p.runs[0]
    run.font.name = font; run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = color
    return box


def title(slide, eyebrow, heading, subtitle=None):
    add_text(slide, eyebrow.upper(), 0.65, 0.62, 11.8, 0.32, 12, TEAL, True)
    add_text(slide, heading, 0.65, 1.00, 12.0, 0.72, 30, WHITE, True)
    if subtitle:
        add_text(slide, subtitle, 0.68, 1.72, 11.7, 0.54, 14, MUTED)


def rounded(slide, x, y, w, h, color=PANEL, radius=True, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = color
    if line:
        shape.line.color.rgb = line; shape.line.width = Pt(1.3)
    else:
        shape.line.fill.background()
    return shape


def bullet_list(slide, items, x, y, w, h, size=17, color=WHITE, accent=TEAL, gap=7):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08); tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"•  {item}"; p.space_after = Pt(gap); p.font.name = "Aptos"; p.font.size = Pt(size); p.font.color.rgb = color
    return box


def metric_card(slide, x, y, label, value, caption, color=BLUE):
    rounded(slide, x, y, 2.45, 1.33, PANEL2)
    add_text(slide, label, x + .18, y + .14, 2.0, .24, 11, MUTED, True)
    add_text(slide, value, x + .18, y + .42, 2.0, .42, 25, color, True)
    add_text(slide, caption, x + .18, y + .91, 2.05, .27, 10, MUTED)


def add_picture(slide, path, x, y, w=None, h=None):
    kwargs = {}
    if w is not None: kwargs["width"] = Inches(w)
    if h is not None: kwargs["height"] = Inches(h)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kwargs)


def new_slide(prs, number, section="VOLT MIZE × INFORMATION RETRIEVAL"):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, number, section); return slide


def model_slide(prs, number, datatype, name, idea, why, screenshot, accent=BLUE):
    slide = new_slide(prs, number, datatype.upper())
    title(slide, f"MODEL {number - 6 if datatype == 'Unstructured text' else number - 11}", name, idea)
    rounded(slide, .65, 2.32, 4.0, 4.48, PANEL)
    add_text(slide, "FEYNMAN VERSION", .92, 2.62, 3.2, .3, 12, TEAL, True)
    bullet_list(slide, why, .88, 3.04, 3.42, 2.55, 16)
    add_text(slide, "What comes out", .92, 5.73, 3.1, .3, 12, MUTED, True)
    add_text(slide, "A repeatable set or ranked list.", .92, 6.08, 3.22, .53, 14, WHITE)
    rounded(slide, 4.92, 2.32, 7.77, 4.48, RGBColor(10, 24, 40), line=accent)
    add_picture(slide, ART / screenshot, 5.14, 2.58, w=7.34, h=4.05)
    return slide


def query_strip(slide, query: str, rule: str, structured: bool = False):
    rounded(slide, .72, 2.08, 11.88, .68, PANEL2, line=TEAL if structured else BLUE)
    add_text(slide, "QUERY", .94, 2.28, .72, .22, 11, TEAL, True)
    add_text(slide, query, 1.67, 2.22, 6.48, .34, 16, WHITE, True)
    add_text(slide, rule, 8.28, 2.23, 3.98, .32, 13, AMBER, True, align=PP_ALIGN.RIGHT)


def score_row(slide, y, doc_id, evidence, calculation, score, relevant=True, accent=BLUE):
    rounded(slide, .72, y, 8.33, .82, PANEL if relevant else RGBColor(22, 35, 51))
    add_text(slide, doc_id, .93, y + .18, .70, .32, 17, GREEN if relevant else AMBER, True)
    add_text(slide, evidence, 1.69, y + .13, 4.17, .50, 13, WHITE, True)
    add_text(slide, calculation, 5.92, y + .15, 2.00, .46, 12, MUTED)
    add_text(slide, score, 8.02, y + .19, .76, .30, 15, accent, True, align=PP_ALIGN.RIGHT)


def ranking_panel(slide, items, note, accent=BLUE):
    rounded(slide, 9.32, 2.98, 3.28, 3.42, PANEL, line=accent)
    add_text(slide, "TOP 3", 9.62, 3.24, 2.50, .27, 12, accent, True)
    for i, (doc_id, score, relevant) in enumerate(items):
        y = 3.72 + i * .64
        rounded(slide, 9.56, y, 2.78, .48, PANEL2)
        add_text(slide, f"{i + 1}", 9.74, y + .11, .30, .24, 13, MUTED, True)
        add_text(slide, doc_id, 10.12, y + .09, .72, .26, 15, GREEN if relevant else AMBER, True)
        add_text(slide, score, 11.15, y + .11, .92, .23, 12, WHITE, True, align=PP_ALIGN.RIGHT)
    add_text(slide, note, 9.60, 5.79, 2.44, .43, 11, MUTED)


def lesson_strip(slide, text, color=TEAL):
    rounded(slide, .72, 6.55, 11.88, .55, PANEL2)
    add_text(slide, "WHY", .95, 6.72, .55, .20, 11, color, True)
    add_text(slide, text, 1.55, 6.67, 10.62, .29, 13, WHITE, True)


def process_slide(prs, number, datatype, name, subtitle, query, rule, rows, ranking, note, lesson, accent=BLUE):
    slide = new_slide(prs, number, datatype.upper())
    title(slide, "QUERY → EVIDENCE → SCORE → RANK", name, subtitle)
    query_strip(slide, query, rule, datatype == "Structured text")
    for index, row in enumerate(rows):
        score_row(slide, 3.03 + index * 1.02, *row, accent=accent)
    ranking_panel(slide, ranking, note, accent)
    lesson_strip(slide, lesson)
    return slide


def add_table(slide, rows, cols, x, y, w, h, data, widths=None, font_size=12):
    table = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h)).table
    if widths:
        for i, width in enumerate(widths): table.columns[i].width = Inches(width)
    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c); cell.text = str(data[r][c]); cell.margin_left = cell.margin_right = Inches(.08)
            cell.fill.solid(); cell.fill.fore_color.rgb = PANEL2 if r == 0 else PANEL
            cell.border_left = None if hasattr(cell, "border_left") else None
            for p in cell.text_frame.paragraphs:
                p.font.name = "Aptos"; p.font.size = Pt(font_size); p.font.color.rgb = TEAL if r == 0 else WHITE; p.font.bold = r == 0
                p.alignment = PP_ALIGN.LEFT
    return table


def build():
    prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)

    # 1 — Cover
    s = new_slide(prs, 1)
    add_text(s, "INFORMATION RETRIEVAL • FYP-BASED IMPLEMENTATION", .72, .72, 11.7, .35, 13, TEAL, True)
    add_text(s, "Finding the right energy evidence", .72, 1.37, 11.65, 1.15, 40, WHITE, True)
    add_text(s, "Applying 7 retrieval models to VoltMize", .75, 2.60, 10.7, .55, 23, BLUE, True)
    rounded(s, .72, 3.55, 11.88, 2.14, PANEL)
    add_text(s, "QUESTION", 1.04, 3.92, 1.6, .25, 11, MUTED, True)
    add_text(s, "When a factory user describes a problem, which past incident or diagnostic record should appear first?", 1.04, 4.22, 10.7, 1.05, 21, WHITE, True)
    add_text(s, "Course presentation • 12–13 October 2026", 1.04, 5.22, 6.0, .3, 12, MUTED)

    # 2 — FYP problem
    s = new_slide(prs, 2)
    title(s, "01 • FYP PROBLEM", "VoltMize turns meter streams into actionable evidence")
    labels = [("01", "INGEST", "Factory meter readings"), ("02", "DETECT", "Abnormal consumption"), ("03", "EXPLAIN", "Likely cause + context"), ("04", "ACT", "Recommended response")]
    for i, (num, head, body) in enumerate(labels):
        x = .72 + i * 3.08; rounded(s, x, 2.55, 2.7, 2.36, PANEL)
        add_text(s, num, x + .2, 2.76, .46, .38, 19, TEAL, True)
        add_text(s, head, x + .2, 3.31, 2.1, .34, 17, WHITE, True)
        add_text(s, body, x + .2, 3.82, 2.13, .68, 14, MUTED)
    rounded(s, .72, 5.35, 11.88, 1.10, PANEL2, line=TEAL)
    add_text(s, "IR retrieval problem", 1.02, 5.62, 2.2, .28, 14, TEAL, True)
    add_text(s, "Retrieve the most relevant historical evidence for a natural-language factory-energy query.", 3.18, 5.57, 8.87, .42, 18, WHITE, True)

    # 3 — formulation
    s = new_slide(prs, 3)
    title(s, "02 • RETRIEVAL REQUIREMENT", "One project question, two kinds of evidence")
    data = [
        ["Element", "Unstructured text", "Structured text"],
        ["Query", "“compressor abnormal high energy night shift”", "“weekend no production shutdown consumption”"],
        ["Document / item", "Technician incident report", "Diagnostic JSON record"],
        ["Result", "Ranked reports", "Ranked records / regions"],
        ["Success", "Relevant incidents in top 3", "Correct diagnosis and action in top 3"],
    ]
    add_table(s, 5, 3, .72, 2.18, 11.88, 3.70, data, widths=[2.1, 4.86, 4.92], font_size=13)
    add_text(s, "Why two datasets?", .82, 6.20, 2.2, .28, 13, AMBER, True)
    add_text(s, "The models make different assumptions about document structure, so a fair demo gives each family the data shape it was designed for.", 2.72, 6.14, 9.55, .46, 14, WHITE)

    # 4 — map
    s = new_slide(prs, 4)
    title(s, "03 • MODEL MAP", "From course concepts to VoltMize datasets")
    rounded(s, .72, 2.18, 5.75, 4.48, PANEL)
    add_text(s, "UNSTRUCTURED INCIDENT REPORTS", 1.04, 2.52, 4.9, .34, 14, BLUE, True)
    bullet_list(s, ["Boolean — exact presence", "Vector Space — TF‑IDF similarity", "BIM — probability from binary evidence", "BM25 — term frequency + rarity + length"], 1.02, 3.03, 4.78, 2.55, 17)
    rounded(s, 6.75, 2.18, 5.85, 4.48, PANEL)
    add_text(s, "STRUCTURED DIAGNOSTIC RECORDS", 7.07, 2.52, 4.95, .34, 14, TEAL, True)
    bullet_list(s, ["Overlapped Lists — terms together in one region", "Non‑Overlapped Lists — terms across regions", "Proximal Nodes — nearby fields / nodes"], 7.05, 3.03, 4.86, 2.55, 17)
    add_text(s, "Not treated as retrieval models: clustering and classification are supporting organization tasks.", 7.08, 5.83, 4.78, .52, 12, MUTED)

    # 5 — evaluation
    s = new_slide(prs, 5)
    title(s, "04 • EVALUATION", "Five judged queries per data type • Top‑3 evaluation", "Ground truth was written before scoring: each query has an explicit relevant-document list.")
    metric_card(s, .72, 2.48, "PRECISION@3", "hits ÷ 3", "How clean are the first 3?", BLUE)
    metric_card(s, 3.29, 2.48, "RECALL@3", "hits ÷ all", "How much did we recover?", TEAL)
    metric_card(s, 5.86, 2.48, "F1@3", "P + R", "Precision + recall together", GREEN)
    metric_card(s, 8.43, 2.48, "MRR", "first-hit rank", "How soon is first good hit?", AMBER)
    metric_card(s, 11.00, 2.48, "nDCG@3", "rank score", "Rewards good ordering", RED)
    rounded(s, .72, 4.32, 11.88, 1.78, PANEL)
    add_text(s, "Test discipline", 1.02, 4.65, 2.0, .3, 14, TEAL, True)
    add_text(s, "Same tokenization • same queries • same relevance judgments • deterministic runs", 3.10, 4.61, 8.8, .74, 18, WHITE, True)
    add_text(s, "This is a small classroom benchmark, so the scores demonstrate behavior—not production readiness.", 3.10, 5.43, 8.8, .42, 13, MUTED)

    # 6 — unstructured dataset
    s = new_slide(prs, 6)
    title(s, "DATA TYPE A", "Unstructured text: 15 technician incident reports", "Fictional but traceable to VoltMize events: energy anomalies, context, diagnosis, and maintenance action.")
    rounded(s, .72, 2.25, 7.25, 3.77, PANEL)
    add_text(s, "U01 • Compressor‑1 night shift anomaly", 1.02, 2.62, 6.6, .34, 19, BLUE, True)
    add_text(s, "“During the night shift Compressor‑1 drew unusually high energy. Power stayed above 92 kW while production was idle. Inspect unload valve leakage and the pressure setpoint.”", 1.02, 3.14, 6.48, 1.47, 18, WHITE)
    add_text(s, "Document = title + free-text note", 1.02, 5.18, 4.9, .32, 13, TEAL, True)
    rounded(s, 8.25, 2.25, 4.35, 3.77, PANEL2)
    add_text(s, "WHY IT FITS", 8.58, 2.62, 3.5, .3, 13, TEAL, True)
    bullet_list(s, ["Technicians naturally write prose", "Term frequency and rarity matter", "No reliable fields are required", "Search supports incident triage"], 8.50, 3.08, 3.55, 2.25, 15)
    add_text(s, "5 queries • 15 documents • qrels included", .76, 6.35, 5.8, .3, 13, MUTED)

    process_slide(
        prs, 7, "Unstructured text", "Boolean Retrieval",
        "OR selects a document when any query term is present; every selected document ties.",
        "compressor abnormal high energy night shift", "ANY MATCH → score 1",
        [
            ("U01", "✓ compressor  ✓ high  ✓ energy  ✓ night  ✓ shift", "5 matches—but Boolean ignores count", "1.000", True),
            ("U02", "✓ shift", "1 match receives same score", "1.000", False),
            ("U03", "✓ shift", "1 match receives same score", "1.000", False),
        ],
        [("U01", "1.000", True), ("U02", "1.000", False), ("U03", "1.000", False)],
        "Tie shown in document-ID order.",
        "Boolean answers MATCH / NO MATCH; it does not know that five matches are stronger than one."
    )
    process_slide(
        prs, 8, "Unstructured text", "Vector Space Model",
        "TF‑IDF turns the query and reports into vectors; cosine similarity ranks their direction.",
        "compressor abnormal high energy night shift", "TF‑IDF → COSINE",
        [
            ("U01", "5 terms • compressor×2 • night×2 • shift×2", "strong shared weighted direction", "0.4365", True),
            ("U06", "abnormal + compressor + shift", "rare ‘abnormal’ adds high IDF", "0.2413", True),
            ("U11", "compressor×2 + night", "fewer terms, still similar", "0.2093", True),
        ],
        [("U01", "0.4365", True), ("U06", "0.2413", True), ("U11", "0.2093", True)],
        "Largest cosine appears first.",
        "Frequency and rarity shape the vectors; cosine compares the complete term-weight pattern."
    )
    process_slide(
        prs, 9, "Unstructured text", "Binary Independence Model (BIM)",
        "Each term is binary evidence; present rare terms contribute larger RSJ weights.",
        "compressor abnormal high energy night shift", "PRESENT? × RARITY → SUM",
        [
            ("U01", "1 0 1 1 1 1  → five present terms", "sum RSJ weights", "4.7107", True),
            ("U06", "1 1 0 0 0 1  → includes rare ‘abnormal’", "rare evidence lifts score", "4.4799", True),
            ("U11", "1 0 0 0 1 0  → two present terms", "repetition is ignored", "2.9594", True),
        ],
        [("U01", "4.7107", True), ("U06", "4.4799", True), ("U11", "2.9594", True)],
        "Binary vector order follows query terms.",
        "BIM ranks by the strength of present evidence, not by how many times a word repeats."
    )
    process_slide(
        prs, 10, "Unstructured text", "BM25",
        "For every matching term: rarity × saturated frequency × length normalization.",
        "compressor abnormal high energy night shift", "IDF × TF SATURATION × LENGTH",
        [
            ("U01", "5 terms • compressor×2 • night×2 • shift×2", "rarity + repeat boost + length", "7.9923", True),
            ("U06", "abnormal + compressor + shift", "rare terms; each occurs once", "5.2178", True),
            ("U11", "compressor×2 + night", "repeat boost, lower coverage", "4.0005", True),
        ],
        [("U01", "7.9923", True), ("U06", "5.2178", True), ("U11", "4.0005", True)],
        "Scores use k1=1.5 and b=0.75.",
        "BM25 rewards useful repetition but limits spam, then corrects for document length.", TEAL
    )

    # 11 — annotated implementation
    s = new_slide(prs, 11, "UNSTRUCTURED TEXT • IMPLEMENTATION")
    title(s, "CODE → FORMULA → RANK", "Where BM25 scoring happens in the real code", "The highlighted lines are the implementation that generated the scores on the previous slide.")
    add_picture(s, ART / "bm25_code_highlight.png", .72, 2.20, w=8.05, h=4.72)
    rounded(s, 9.03, 2.20, 3.57, 4.72, PANEL)
    callouts = [
        ("① TOKENIZE", "Line 22 turns the query into terms."),
        ("② NORMALIZE", "Line 25 measures document length."),
        ("③ SCORE", "Lines 31–32 compute IDF and add each BM25 term score."),
        ("④ RANK", "Line 35 sorts highest score first."),
    ]
    for i, (head, body) in enumerate(callouts):
        y = 2.55 + i * .98
        add_text(s, head, 9.34, y, 2.65, .25, 12, TEAL if i == 2 else BLUE, True)
        add_text(s, body, 9.34, y + .31, 2.72, .52, 12, WHITE)
    add_text(s, "Same code → same scores → same top 3", 9.34, 6.50, 2.72, .26, 12, GREEN, True)

    # 12 comparison
    s = new_slide(prs, 12)
    title(s, "UNSTRUCTURED COMPARISON", "Ranking changes everything", "Averages across UQ1–UQ5; higher is better.")
    add_picture(s, ART / "unstructured_comparison.png", .72, 2.16, w=8.25, h=4.15)
    rounded(s, 9.25, 2.16, 3.35, 4.15, PANEL)
    add_text(s, "RESULT", 9.58, 2.50, 2.55, .3, 12, TEAL, True)
    add_text(s, "0.923", 9.56, 3.00, 2.4, .55, 32, WHITE, True)
    add_text(s, "nDCG@3 for VSM, BIM & BM25", 9.58, 3.61, 2.46, .58, 14, MUTED)
    add_text(s, "Selection", 9.58, 4.47, 2.45, .28, 12, AMBER, True)
    add_text(s, "BM25", 9.58, 4.84, 2.45, .42, 24, WHITE, True)
    add_text(s, "Tie broken by practical robustness: frequency saturation and length normalization.", 9.58, 5.40, 2.48, .65, 12, MUTED)

    # 13 structured dataset
    s = new_slide(prs, 13)
    title(s, "DATA TYPE B", "Structured text: 12 diagnostic JSON records", "Each record preserves the stages VoltMize needs to explain an anomaly.")
    fields = [("equipment", "Compressor‑1"), ("summary", "High energy during night shift"), ("symptoms", "94 kW • idle • cycling"), ("meter_context", "night • 488 kWh"), ("probable_cause", "unload valve leakage"), ("action", "inspect valve; reduce setpoint")]
    for i, (key, value) in enumerate(fields):
        y = 2.22 + i * .64; rounded(s, .78, y, 7.18, .50, PANEL if i % 2 == 0 else PANEL2)
        add_text(s, key, 1.02, y + .11, 1.78, .24, 12, TEAL, True)
        add_text(s, value, 2.95, y + .09, 4.65, .28, 14, WHITE)
    rounded(s, 8.25, 2.22, 4.35, 3.70, PANEL)
    add_text(s, "WHY STRUCTURE MATTERS", 8.58, 2.57, 3.5, .3, 13, TEAL, True)
    bullet_list(s, ["The same term can occur in different fields", "Cause and action may be separated", "Region co‑occurrence changes meaning", "Tree distance can express closeness"], 8.50, 3.02, 3.57, 2.35, 15)

    process_slide(
        prs, 14, "Structured text", "Overlapped Lists",
        "Count query terms inside each field; only the best single field becomes the score basis.",
        "night shift compressor high energy cause action", "MAX MATCHES IN ONE FIELD",
        [
            ("S01", "summary: night + shift + high + energy", "best field = 4 → 4 + 4/7", "4.5714", True),
            ("S03", "meter_context: energy + shift", "best field = 2 → 2 + 2/7", "2.2857", False),
            ("S06", "meter_context: energy + night", "best field = 2 → 2 + 2/7", "2.2857", False),
        ],
        [("S01", "4.5714", True), ("S03", "2.2857", False), ("S06", "2.2857", False)],
        "S02 is relevant, but its terms are split across fields.",
        "This model rewards co-occurrence inside one region and ignores evidence scattered elsewhere."
    )
    process_slide(
        prs, 15, "Structured text", "Non‑Overlapped Lists",
        "Merge unique matches from every field, then divide matched query terms by query length.",
        "night shift compressor high energy cause action", "UNION ACROSS FIELDS ÷ 7",
        [
            ("S01", "equipment: compressor • summary: night shift high energy", "5 unique terms ÷ 7", "0.7143", True),
            ("S03", "symptoms: high • context: energy shift", "3 unique terms ÷ 7", "0.4286", False),
            ("S02", "equipment: compressor • symptoms/context: shift", "2 unique terms ÷ 7", "0.2857", True),
        ],
        [("S01", "0.7143", True), ("S03", "0.4286", False), ("S02", "0.2857", True)],
        "Distributed evidence lets S02 enter the top 3.",
        "Unlike overlap, a match can be assembled from equipment, symptoms, context, cause, and action.", TEAL
    )
    process_slide(
        prs, 16, "Structured text", "Proximal Nodes",
        "Coverage finds the terms; node distance rewards matches that occur in the same or nearby fields.",
        "night shift compressor high energy cause action", "2×COVERAGE + Σ 1/(1+DISTANCE)",
        [
            ("S01", "equipment[0] ↔ summary[1] ↔ context[3]", "5/7 coverage + many close pairs", "9.4286", True),
            ("S03", "high[2] ↔ energy,shift[3]", "3/7 coverage + 1+.5+.5", "2.8571", False),
            ("S06", "energy[1,3] + night[3]", "2/7 coverage + same-node pair", "1.5714", False),
        ],
        [("S01", "9.4286", True), ("S03", "2.8571", False), ("S06", "1.5714", False)],
        "Node numbers follow the six-field record order.",
        "Same node gives bonus 1; adjacent nodes .5; farther evidence contributes progressively less."
    )

    # 17 comparison
    s = new_slide(prs, 17)
    title(s, "STRUCTURED COMPARISON", "Distributed evidence favors Non‑Overlapped Lists", "Averages across SQ1–SQ5; higher is better.")
    add_picture(s, ART / "structured_comparison.png", .72, 2.16, w=8.25, h=4.15)
    rounded(s, 9.25, 2.16, 3.35, 4.15, PANEL)
    add_text(s, "BEST nDCG@3", 9.58, 2.50, 2.55, .3, 12, TEAL, True)
    add_text(s, "0.968", 9.56, 3.00, 2.4, .55, 32, GREEN, True)
    add_text(s, "Non‑Overlapped Lists", 9.58, 3.62, 2.46, .45, 17, WHITE, True)
    add_text(s, "Why?", 9.58, 4.47, 2.45, .28, 12, AMBER, True)
    add_text(s, "VoltMize queries mix equipment + symptom + context + action. Those clues live in different fields.", 9.58, 4.84, 2.48, 1.04, 13, MUTED)

    # 18 decision
    s = new_slide(prs, 18)
    title(s, "MODEL DECISION", "There is no honest single winner across different data types", "We select one model per evidence shape, then choose the measured overall leader for the final demo.")
    rounded(s, .72, 2.35, 5.75, 3.56, PANEL)
    add_text(s, "FREE-TEXT REPORTS", 1.04, 2.72, 4.7, .3, 13, BLUE, True)
    add_text(s, "BM25", 1.04, 3.25, 3.8, .55, 30, WHITE, True)
    bullet_list(s, ["Tied best measured nDCG@3: 0.923", "Most robust ranking assumptions", "Recommended incident-search baseline"], 1.02, 4.00, 4.65, 1.4, 15)
    rounded(s, 6.75, 2.35, 5.85, 3.56, PANEL, line=TEAL)
    add_text(s, "STRUCTURED RECORDS • OVERALL LEADER", 7.07, 2.72, 4.95, .3, 13, TEAL, True)
    add_text(s, "Non‑Overlapped Lists", 7.07, 3.25, 4.7, .55, 27, GREEN, True)
    bullet_list(s, ["Highest measured nDCG@3: 0.968", "Recall@3: 1.000", "Matches distributed diagnostic evidence"], 7.05, 4.00, 4.72, 1.4, 15)
    # 19 behavior comparison
    s = new_slide(prs, 19)
    title(s, "WHAT WE LEARNED", "The model’s assumptions explain the results")
    data = [
        ["Model behavior", "Helps when…", "Hurts when…"],
        ["Exact presence", "filters are strict", "users describe problems loosely"],
        ["Similarity / probability", "documents are free text", "field structure carries meaning"],
        ["Same-region overlap", "terms must co-occur", "evidence spans fields"],
        ["Across-region evidence", "diagnosis is distributed", "a phrase must stay together"],
        ["Structural proximity", "nearby nodes are meaningful", "field order is only conventional"],
    ]
    add_table(s, 6, 3, .72, 2.15, 11.88, 3.95, data, widths=[3.1, 4.25, 4.53], font_size=13)
    add_text(s, "Core lesson", .83, 6.37, 1.5, .3, 13, AMBER, True)
    add_text(s, "Choose a retrieval model because its assumptions match the document—not because its name sounds advanced.", 2.35, 6.31, 9.75, .40, 16, WHITE, True)

    # 20 query bank
    s = new_slide(prs, 20)
    title(s, "APPENDIX • QUERY BANK", "Ten VoltMize questions used for evaluation")
    left = ["UQ1  compressor abnormal high energy night shift", "UQ2  low power factor motor reactive energy", "UQ3  weekend idle consumption no production", "UQ4  temperature cooling chiller excess energy", "UQ5  missing meter readings communication"]
    right = ["SQ1  night shift compressor high energy cause action", "SQ2  low power factor reactive motor capacitor", "SQ3  weekend no production shutdown consumption", "SQ4  temperature chiller excess energy cause", "SQ5  missing meter readings communication action"]
    rounded(s, .72, 2.15, 5.75, 4.38, PANEL); add_text(s, "UNSTRUCTURED", 1.04, 2.51, 4.7, .3, 13, BLUE, True); bullet_list(s, left, 1.00, 2.99, 4.95, 2.95, 14, gap=13)
    rounded(s, 6.75, 2.15, 5.85, 4.38, PANEL); add_text(s, "STRUCTURED", 7.07, 2.51, 4.9, .3, 13, TEAL, True); bullet_list(s, right, 7.03, 2.99, 5.02, 2.95, 14, gap=13)

    # 21 conclusion
    s = new_slide(prs, 21)
    add_text(s, "CONCLUSION", .72, .82, 11.8, .35, 13, TEAL, True)
    add_text(s, "From meter data to the right evidence", .72, 1.42, 11.7, .75, 36, WHITE, True)
    add_text(s, "We connected course theory to a working, measured retrieval component for VoltMize.", .75, 2.35, 10.9, .55, 19, MUTED)
    rounded(s, .72, 3.30, 11.88, 1.30, PANEL2, line=TEAL)
    add_text(s, "FINAL TAKEAWAY", 1.04, 3.59, 2.2, .28, 12, TEAL, True)
    add_text(s, "BM25 for incident prose. Non‑Overlapped Lists for structured diagnosis.", 3.24, 3.49, 8.65, .82, 18, WHITE, True)
    add_text(s, "Retrieve → rank → evaluate → explain", .72, 5.36, 11.88, .52, 24, BLUE, True, align=PP_ALIGN.CENTER)
    add_text(s, "Questions?", .72, 6.29, 11.88, .45, 18, WHITE, True, align=PP_ALIGN.CENTER)

    target = OUT / "VoltMize_IR_Presentation.pptx"
    prs.save(target)
    print(f"Saved {len(prs.slides)} slides to {target}")


if __name__ == "__main__":
    build()
