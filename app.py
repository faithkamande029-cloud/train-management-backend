from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes import api
import os

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///railway.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# ─── CORS Configuration ──────────────────────────────────────
CORS(
    app,
    origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    supports_credentials=True,        # fixes the credentials error
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)

db.init_app(app)
migrate = Migrate(app, db)

# Register API blueprint (routes are prefixed with /api)
app.register_blueprint(api)

# Root route
@app.route("/")
def index():
    return {
        "message": "Train Management API is running",
        "endpoints": [
            "/api/trains",
            "/api/stations",
            "/api/schedules",
            "/api/bookings",
            "/api/users",
            "/api/login",
            "/me"
        ]
    }

if __name__ == "__main__":
    app.run(debug=True, port=5000)