import os

# ─── MySQL Configuration ───────────────────────────────────────────
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "db": os.getenv("DB_NAME", "pashucare"),
    "charset": "utf8mb4",
    "cursorclass": "DictCursor",
}

# ─── Flask / Session ───────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "pashucare-secret-2026")
SESSION_TYPE = "filesystem"          # sessions stored on disk
SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), "flask_session_data")
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30   # 30 days in seconds
