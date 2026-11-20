import os
import subprocess
from pathlib import Path

def main() -> None:

    root = Path(__file__).resolve().parents[0]
    #app_file = root / "src" / "user_data_manager" / "main.py"

    print('Authenticating in Azure...')
    print('\t=> Checking if already authenticated in shell session...')

    if subprocess.run(['az', 'account', 'show'], capture_output=True, text=True).returncode != 0:
        subprocess.run(['az', 'login'], cwd=root)
    else:
        print('User already authenticated before!')

    print(f'Running Azure Functions Tool in {root}')
    subprocess.run(['func', 'start', 'host'], cwd=root)
