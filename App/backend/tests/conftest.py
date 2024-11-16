import os
import sys
from pathlib import Path
BACKEND_ROOT = Path(__file__).resolve().parents[2].joinpath("backend")
sys.path.insert(0, BACKEND_ROOT.as_posix())
os.chdir(BACKEND_ROOT)
print(f"sys path = {sys.path}")
