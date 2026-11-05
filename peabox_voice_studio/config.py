from pathlib import Path

APP_NAME = "PeaBox Voice Studio"
VERSION = "0.03.12"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
OUTPUTS_DIR = BASE_DIR / "outputs"
MODELS_DIR = BASE_DIR / "models"
MAX_SCRIPT_CHARS = 200_000
MAX_BLOCK_CHARS = 20_000
MAX_UPLOAD_BYTES = 500 * 1024 * 1024

for folder in (DATA_DIR, PROJECTS_DIR, OUTPUTS_DIR, MODELS_DIR):
    folder.mkdir(parents=True, exist_ok=True)
