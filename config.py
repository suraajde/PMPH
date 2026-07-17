from pathlib import Path

# Project Information
APP_NAME = "PMPH"
APP_FULL_NAME = "Portfolio Manager & Portfolio Health"
VERSION = "0.1.0"

# Root Directory
PROJECT_ROOT = Path(__file__).parent

# Project Folders
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = PROJECT_ROOT / "database"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"

# Database
DATABASE_NAME = "pmph.db"
DATABASE_PATH = DATABASE_DIR / DATABASE_NAME