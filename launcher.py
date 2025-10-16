import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

# Add local lib and modules folders to the import path
sys.path.insert(0, str(BASE_DIR / "lib"))
sys.path.insert(0, str(BASE_DIR / "modules"))

# Import your main entry point
import main

if __name__ == "__main__":
    main.runApp()