
import os
import sys
from pathlib import Path

def main() -> None:
    root = Path(__file__).resolve().parents[2]
    app_file = root / "src" / "control_de_cultivos" / "main.py"
    os.execvp("streamlit", ["streamlit", "run", str(app_file)])
