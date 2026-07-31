import os

from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db, User
from routes import api
from flask_cors import CORS
import structlog


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


app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get(
    "SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = os.environ.get(
    "SESSION_COOKIE_SECURE", "False") == "True"
app.config["SESSION_COOKIE_HTTPONLY"] = os.environ.get(
    "SESSION_COOKIE_HTTPONLY", "True") == "True"


CORS_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")
CORS(
    app, 
    supports_credentials=True,
    origins=[origin.strip() for origin in CORS_ORIGINS if origin.strip()],
)

db.init_app(app=app)

app.register_blueprint(api)


@app.get("/")
def index():
    """A public response for the service URL and Render health checks."""
    return jsonify({
        "service": "train-management-backend",
        "status": "ok",
        "api": "/api",
        "health": "/health",
    })


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
        content_type=request.headers.get("Content-Type")
    )


@app.before_request
def check_if_authenticated():
    public_routes = {
        "/api/register",
        "/api/login",
        "/",
        "/health",
    }
    if request.method == "OPTIONS" or request.path in public_routes:
        return

    if not session.get("user_id") and request.endpoint:
        return {
            "status": 401,
            "message": "Not authenticated. Login to access resource",
        }, 401
