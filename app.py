from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
import secrets
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass


load_dotenv()

app = Flask(__name__)

# ======================
# BASIC CONFIG
# ======================
app.secret_key = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ======================
# ENV DETECTION
# ======================
is_render = bool(os.environ.get("RENDER_EXTERNAL_URL"))
is_vercel = os.environ.get("VERCEL") == "1"

# ======================
# DATABASE URL FETCH
# ======================
database_url = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("POSTGRES_URL")
    or os.environ.get("POSTGRES_URL_NON_POOLING")
    or os.environ.get("POSTGRES_PRISMA_URL")
)

# Fix deprecated postgres:// format
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# ======================
# IMPORTANT FIX (NO SILENT FALLBACK IN PROD)
# ======================
if not database_url:
    if is_render:
        raise RuntimeError(
            "❌ DATABASE_URL is not set on Render. Add PostgreSQL Internal URL in Environment Variables."
        )
    elif is_vercel:
        database_url = "sqlite:////tmp/nurseai.db"
        logging.warning("Using SQLite on Vercel (/tmp)")
    else:
        database_url = "sqlite:///nurseai.db"
        logging.warning("Using local SQLite database")

# ======================
# FLASK CONFIG
# ======================
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if not database_url.startswith("sqlite"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "/tmp/uploads" if (is_render or is_vercel) else "uploads"

# ======================
# DB INIT
# ======================
db = SQLAlchemy(app, model_class=Base)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

with app.app_context():
    import models
    try:
        db.create_all()
        logging.info("Database tables created successfully")
        logging.info(f"DB URL: {database_url}")
    except Exception as e:
        logging.exception("Database initialization failed: %s", e)


# ======================
# ROUTE (FIX YOUR 404 ISSUE)
# ======================
@app.route("/")
def home():
    return "🔥 AI Health App is running successfully on Render!"
