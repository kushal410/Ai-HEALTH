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

database_url = os.environ.get("DATABASE_URL")
# Local-friendly default: SQLite when DATABASE_URL isn't provided.
# This makes the project runnable without provisioning Postgres.
if not database_url:
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
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app, model_class=Base)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    import models
    db.create_all()
    logging.info("Database tables created")
