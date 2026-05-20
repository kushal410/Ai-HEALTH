from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
import secrets
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

is_vercel = os.environ.get("VERCEL") == "1"
is_render = os.environ.get("RENDER") == "true" or bool(os.environ.get("RENDER_EXTERNAL_URL"))

database_url = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("POSTGRES_URL")
    or os.environ.get("POSTGRES_URL_NON_POOLING")
    or os.environ.get("POSTGRES_PRISMA_URL")
)
# Local-friendly default: SQLite when DATABASE_URL isn't provided.
# This makes the project runnable without provisioning Postgres.
if not database_url:
    # In serverless environments, the filesystem is read-only except `/tmp`.
    if is_vercel:
        database_url = "sqlite:////tmp/nurseai.db"
        logging.warning("DATABASE_URL not set; using SQLite database at /tmp/nurseai.db (Vercel)")
    elif is_render:
        database_url = "sqlite:////tmp/nurseai.db"
        logging.warning("DATABASE_URL not set; using SQLite database at /tmp/nurseai.db (Render)")
    else:
        database_url = "sqlite:///nurseai.db"
        logging.warning("DATABASE_URL not set; using SQLite database at nurseai.db")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
if not database_url.startswith("sqlite"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = '/tmp/uploads' if (is_vercel or is_render) else 'uploads'

db = SQLAlchemy(app, model_class=Base)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    import models
    try:
        db.create_all()
        logging.info("Database tables created")
    except Exception as e:
        logging.exception(
            "Database initialization failed. Set DATABASE_URL (or POSTGRES_URL) to a reachable database. Error: %s",
            e,
        )
