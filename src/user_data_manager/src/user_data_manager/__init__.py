import os
import subprocess
from pathlib import Path

def main() -> None:

    root = Path(__file__).resolve().parents[0]
    #app_file = root / "src" / "user_data_manager" / "main.py"

    print('Authenticating in Azure...')
    subprocess.run(['az', 'login'], cwd=root)

    print(f'Running Azure Functions Tool in {root}')
    subprocess.run(['func', 'start', 'host'], cwd=root)
