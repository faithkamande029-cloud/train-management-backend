import os

from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db, User
from routes import api
from flask_cors import CORS
import structlog
from urllib.parse import urlparse


load_dotenv()

app = Flask(__name__)
# app.secret_key = "hello"

log = structlog.get_logger()

# app config
database_uri = os.environ.get("DATABASE_URI")
# The project depends on psycopg v3, so explicitly select that SQLAlchemy
# driver when a standard PostgreSQL URL is supplied by Render or Neon.
if database_uri and database_uri.startswith("postgresql://"):
    database_uri = database_uri.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


migrate = Migrate(app=app, db=db)


is_production = os.environ.get("FLASK_ENV", "development").lower() == "production"
app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get(
    "SESSION_COOKIE_SAMESITE", "None" if is_production else "Lax"
)
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get(
        "SESSION_COOKIE_SECURE", "True" if is_production else "False"
    ).lower()
    == "true"
)
app.config["SESSION_COOKIE_HTTPONLY"] = (
    os.environ.get("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
)


def parse_origins(*origin_sources):
    origins = []
    for source in origin_sources:
        if not source:
            continue
        for origin in source.split(","):
            trimmed = origin.strip()
            if not trimmed:
                continue
            parsed = urlparse(trimmed)
            if parsed.scheme and parsed.netloc:
                cleaned = f"{parsed.scheme}://{parsed.netloc}"
            else:
                cleaned = trimmed
            if cleaned not in origins:
                origins.append(cleaned)
    return origins


allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")
cors_origin = os.environ.get("CORS_ORIGIN", "")
CORS_ORIGINS = parse_origins(allowed_origins, cors_origin)
CORS(
    app,
    supports_credentials=True,
    origins=CORS_ORIGINS,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

db.init_app(app=app)

app.register_blueprint(api)


@app.get("/favicon.ico")
def favicon():
    """Prevent browser favicon requests from producing 404 noise."""
    return "", 204


@app.get("/")
def index():
    """A public response for the service URL and Render health checks."""
    return jsonify(
        {
            "service": "train-management-backend",
            "status": "ok",
            "api": "/api",
            "health": "/health",
        }
    )


@app.get("/health")
def health_check():
    """Report that the web process is available without requiring a session."""
    return jsonify({"status": "ok"})


@app.before_request
def log_request():
    log.info(
        "request",
        method=request.method,
        path=request.path,
        content_type=request.headers.get("Content-Type"),
    )


@app.before_request
def check_if_authenticated():
    public_routes = {
        "/",
        "/health",
        "/favicon.ico",
        "/api/register",
        "/api/login",
        "/api/check-session",
    }
    public_prefixes = (
        "/api/trains",
        "/api/stations",
        "/api/schedules",
    )

    if request.method == "OPTIONS":
        return

    if request.endpoint is None:
        return

    if (
        request.path in public_routes
        or request.path.startswith("/static/")
        or any(request.path.startswith(prefix) for prefix in public_prefixes)
    ):
        return

    if not session.get("user_id"):
        return {
            "status": 401,
            "message": "Not authenticated. Login to access resource",
        }, 401
