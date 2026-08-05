import os
from urllib.parse import urlparse

from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes import api
import structlog

load_dotenv()

app = Flask(__name__)

# ─── Logging ──────────────────────────────────────────────────
log = structlog.get_logger()

# ─── Database Configuration ─────────────────────────────────
database_uri = os.environ.get("DATABASE_URL")
# The project depends on psycopg v3, so explicitly select that SQLAlchemy
# driver when a standard PostgreSQL URL is supplied by Render or Neon.
if database_uri and database_uri.startswith("postgresql://"):
    database_uri = database_uri.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri or "sqlite:///railway.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

# ─── Session Configuration ──────────────────────────────────
is_production = os.environ.get("FLASK_ENV", "development").lower() == "production"
app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get(
    "SESSION_COOKIE_SAMESITE", "None" if is_production else "Lax"
)
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("SESSION_COOKIE_SECURE", "True" if is_production else "False").lower()
    == "true"
)
app.config["SESSION_COOKIE_HTTPONLY"] = (
    os.environ.get("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
)

# ─── CORS Configuration ──────────────────────────────────────
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

# Fallback origins for local development
if not CORS_ORIGINS:
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

CORS(
    app,
    supports_credentials=True,
    origins=CORS_ORIGINS,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ─── Database & Migrations ──────────────────────────────────
db.init_app(app)
migrate = Migrate(app, db)

# ─── Register API Blueprint ─────────────────────────────────
app.register_blueprint(api)

# ─── Routes ──────────────────────────────────────────────────
@app.get("/favicon.ico")
def favicon():
    """Prevent browser favicon requests from producing 404 noise."""
    return "", 204

@app.get("/")
def index():
    """A public response for the service URL and Render health checks."""
    return jsonify({
        "service": "train-management-backend",
        "status": "ok",
        "api": "/api",
        "health": "/health",
        "endpoints": [
            "/api/trains",
            "/api/stations",
            "/api/schedules",
            "/api/bookings",
            "/api/users",
            "/api/login",
            "/api/me"
        ]
    })

@app.get("/health")
def health_check():
    """Report that the web process is available without requiring a session."""
    return jsonify({"status": "ok"})

# ─── Request Logging ────────────────────────────────────────
@app.before_request
def log_request():
    log.info(
        "request",
        method=request.method,
        path=request.path,
        content_type=request.headers.get("Content-Type"),
    )

# ─── Authentication Check ──────────────────────────────────
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

# ─── Run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)