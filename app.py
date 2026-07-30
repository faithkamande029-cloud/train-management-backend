import os

from flask import Flask, request, session
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
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///railway.db"

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
    }
    if request.path in public_routes:
        return

    if not session.get("user_id" \
    "") and request.endpoint:
        return {
            "status": 401,
            "message": "Not authenticated. Login to access resource",
        }, 401
    