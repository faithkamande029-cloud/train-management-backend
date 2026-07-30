import os

from flask import Flask, request
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db
from routes import api
from flask_cors import CORS
import structlog


load_dotenv()

app = Flask(__name__)

log = structlog.get_logger()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///railway.db"

migrate = Migrate(app=app, db=db)

CORS_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")
CORS(
    app, 
    supports_credentials=True,
    origins=[origin.strip() for origin in CORS_ORIGINS if origin.strip()],
)

db.init_app(app=app)

app.register_blueprint(api)

@app.before_request
def log_request():
    log.info(
        "request",
        method=request.method, 
        path=request.path,
        content_type=request.headers.get("Content-Type")
    )

PUBLIC_ENDPOINTS = ["login", "register"]

