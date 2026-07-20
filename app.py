from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///railway.db"

migrate = Migrate(app=app, db=db)

db.init_app(app=app)
