"""Rebuild datasets, results, screenshots, charts, and PowerPoint."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parent
for script in ["run_all.py", "build_artifacts.py", "build_presentation.py"]:
    subprocess.run([sys.executable, str(ROOT / script)], check=True)

print("Complete: datasets, results, visual artifacts, and presentation are ready.")
