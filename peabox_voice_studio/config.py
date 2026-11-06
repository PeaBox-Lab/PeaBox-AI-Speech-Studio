from pathlib import Path
APP_NAME = "PeaBox Voice Studio"
VERSION = "0.09.2"
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
MAX_TIMELINE_MIX_SAMPLES = 24_000_000
MAX_BUNDLE_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_BUNDLE_INPUT_BYTES = 600 * 1024 * 1024

DATABASE_PATH = DATA_DIR / "peabox.db"
OPERATIONS_LOG_PATH = DATA_DIR / "operations.jsonl"
MAINTENANCE_PATH = DATA_DIR / "maintenance.json"
BACKUPS_DIR = DATA_DIR / "backups"
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
