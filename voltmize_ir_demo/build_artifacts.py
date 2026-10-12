"""Build presentation-ready screenshots and metric charts from real run results."""
from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

MODELS = [
    ("Boolean", "unstructured_text/boolean_model"),
    ("Vector Space", "unstructured_text/vector_space"),
    ("BIM", "unstructured_text/bim"),
    ("BM25", "unstructured_text/bm25"),
    ("Overlapped Lists", "structured_text/overlapped_lists"),
    ("Non-Overlapped Lists", "structured_text/non_overlapped_lists"),
    ("Proximal Nodes", "structured_text/proximal_nodes"),
]


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def result_screenshot(label: str, folder: Path, query_index: int = 0, output_name: str | None = None) -> None:
    result = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    item = result["queries"][query_index]
    image = Image.new("RGB", (1400, 820), "#07111f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((45, 40, 1355, 780), radius=24, fill="#0d1b2d", outline="#2dd4bf", width=3)
    draw.ellipse((76, 70, 92, 86), fill="#ff5f57")
    draw.ellipse((102, 70, 118, 86), fill="#febc2e")
    draw.ellipse((128, 70, 144, 86), fill="#28c840")
    draw.text((180, 60), f"voltmize-ir > {label}", font=font(30, True), fill="#dbeafe")
    y = 130
    draw.text((85, y), "ACTUAL RUN OUTPUT", font=font(22, True), fill="#2dd4bf")
    y += 55
    for line in textwrap.wrap(f"QUERY: {item['query']}", 76):
        draw.text((85, y), line, font=font(29, True), fill="white")
        y += 40
    draw.text((85, y + 10), f"Judged relevant: {', '.join(item['relevant'])}", font=font(24), fill="#94a3b8")
    y += 80
    for hit in item["top_results"]:
        fill = "#34d399" if hit["document"] in item["relevant"] else "#fbbf24"
        draw.rounded_rectangle((85, y, 1315, y + 76), radius=12, fill="#12263f")
        draw.text((112, y + 19), f"#{hit['rank']}  {hit['document']}", font=font(28, True), fill=fill)
        draw.text((1050, y + 20), f"score {hit['score']:.4f}", font=font(25), fill="#cbd5e1")
        y += 94
    metrics = item["metrics"]
    draw.text((85, 666), f"P@3 {metrics['precision@3']:.3f}   R@3 {metrics['recall@3']:.3f}   MRR {metrics['mrr']:.3f}   nDCG@3 {metrics['ndcg@3']:.3f}", font=font(27, True), fill="#60a5fa")
    output = ART / (output_name or f"{folder.name}_query_output.png")
    image.save(output)


def charts_and_csv(rows: list[dict]) -> None:
    with (ART / "model_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["model", "data_type", "precision@3", "recall@3", "f1@3", "mrr", "ndcg@3"])
        writer.writeheader()
        writer.writerows(rows)

    for data_type, filename, title in [
        ("Unstructured", "unstructured_comparison.png", "Unstructured incident retrieval"),
        ("Structured", "structured_comparison.png", "Structured diagnostic retrieval"),
    ]:
        subset = [row for row in rows if row["data_type"] == data_type]
        labels = [row["model"] for row in subset]
        x = range(len(labels))
        width = 0.24
        fig, ax = plt.subplots(figsize=(11.5, 5.6))
        fig.patch.set_facecolor("#f8fafc")
        ax.set_facecolor("#f8fafc")
        for offset, metric, color in [(-width, "precision@3", "#2563eb"), (0, "recall@3", "#14b8a6"), (width, "ndcg@3", "#f59e0b")]:
            values = [row[metric] for row in subset]
            bars = ax.bar([i + offset for i in x], values, width, label=metric, color=color)
            ax.bar_label(bars, fmt="%.2f", fontsize=9, padding=2)
        ax.set_ylim(0, 1.15)
        ax.set_xticks(list(x), labels, fontsize=10)
        ax.set_ylabel("Score (higher is better)")
        ax.set_title(title, fontsize=17, fontweight="bold")
        ax.legend(ncol=3, loc="upper left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.18)
        fig.tight_layout()
        fig.savefig(ART / filename, dpi=180, bbox_inches="tight")
        plt.close(fig)


def code_screenshot() -> None:
    """Render the real BM25 search function with its scoring lines highlighted."""
    source_path = ROOT / "unstructured_text" / "bm25" / "run.py"
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    selected = list(enumerate(source_lines[20:35], start=21))
    image = Image.new("RGB", (1500, 880), "#07111f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((35, 35, 1465, 845), radius=22, fill="#0d1b2d", outline="#334155", width=2)
    draw.ellipse((67, 65, 83, 81), fill="#ff5f57")
    draw.ellipse((93, 65, 109, 81), fill="#febc2e")
    draw.ellipse((119, 65, 135, 81), fill="#28c840")
    draw.text((170, 53), "unstructured_text/bm25/run.py", font=font(27, True), fill="#dbeafe")
    code_font = font(25)
    number_font = font(22, True)
    y = 118
    for number, line in selected:
        if number in {31, 32}:
            draw.rounded_rectangle((65, y - 7, 1430, y + 40), radius=8, fill="#123c3b", outline="#2dd4bf", width=2)
        elif number in {22, 25, 35}:
            draw.rounded_rectangle((65, y - 7, 1430, y + 40), radius=8, fill="#152a45")
        draw.text((82, y), f"{number:>2}", font=number_font, fill="#64748b")
        draw.text((142, y), line, font=code_font, fill="#f8fafc")
        y += 46
    draw.text((80, 808), "Highlighted lines are read directly from the implementation used for the measured results.", font=font(20), fill="#94a3b8")
    image.save(ART / "bm25_code_highlight.png")


def main() -> None:
    rows = []
    for label, relative in MODELS:
        folder = ROOT / relative
        result_screenshot(label, folder)
        result = json.loads((folder / "results.json").read_text(encoding="utf-8"))
        rows.append({"model": label, "data_type": "Unstructured" if relative.startswith("unstructured") else "Structured", **result["aggregate"]})
    result_screenshot(
        "Non-Overlapped Lists — final selection",
        ROOT / "structured_text/non_overlapped_lists",
        query_index=2,
        output_name="best_model_final_query.png",
    )
    charts_and_csv(rows)
    code_screenshot()
    print(f"Built {len(MODELS)} query screenshots, two charts, and model_comparison.csv in {ART}")


if __name__ == "__main__":
    main()
