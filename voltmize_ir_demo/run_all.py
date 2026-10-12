"""Generate datasets, run every model, and save their real console output."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent
MODELS = [
    "unstructured_text/boolean_model/run.py",
    "unstructured_text/vector_space/run.py",
    "unstructured_text/bim/run.py",
    "unstructured_text/bm25/run.py",
    "structured_text/overlapped_lists/run.py",
    "structured_text/non_overlapped_lists/run.py",
    "structured_text/proximal_nodes/run.py",
]


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "generate_datasets.py")], check=True)
    for relative in MODELS:
        script = ROOT / relative
        completed = subprocess.run([sys.executable, str(script)], check=True, text=True, capture_output=True)
        output_path = script.parent / "console_output.txt"
        output_path.write_text(completed.stdout, encoding="utf-8")
        print(completed.stdout)


if __name__ == "__main__":
    main()
