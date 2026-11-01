import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory: project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "backend" / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "anika-ai-super-secure-session-key-2026")
    
    # SQLite Database
    DB_PATH = BASE_DIR / "instance" / "anika.db"
    os.makedirs(DB_PATH.parent, exist_ok=True)
    
    _raw_db_url = os.getenv("DATABASE_URL")
    if _raw_db_url and _raw_db_url.startswith("sqlite:///"):
        _rel_path = _raw_db_url.replace("sqlite:///", "", 1)
        if not os.path.isabs(_rel_path) and not (_rel_path.startswith(":") or (len(_rel_path) > 1 and _rel_path[1] == ":")):
            _resolved_path = (BASE_DIR / _rel_path).resolve()
            os.makedirs(_resolved_path.parent, exist_ok=True)
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{_resolved_path.as_posix()}"
        else:
            SQLALCHEMY_DATABASE_URI = _raw_db_url
    elif _raw_db_url:
        SQLALCHEMY_DATABASE_URI = _raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Upload settings
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE_MB", "16")) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "pdf"}
    
    # Trained models
    MODEL_DIR = str(BASE_DIR / "backend" / "trained_models")
    os.makedirs(MODEL_DIR, exist_ok=True)
    CATEGORY_MODEL_PATH = os.path.join(MODEL_DIR, "category_model.pkl")
    
    # Dataset path
    DATASET_DIR = str(BASE_DIR / "backend" / "datasets")
    os.makedirs(DATASET_DIR, exist_ok=True)
    DATASET_PATH = os.path.join(DATASET_DIR, "expense_categories_dataset.csv")

    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True in HTTPS production
