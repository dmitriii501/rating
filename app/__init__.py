import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "admin.login"


def create_app() -> Flask:
	"""
	Application factory. Configures Flask, database, login manager, and blueprints.
	"""
	load_dotenv()
	app = Flask(__name__, static_folder="static", template_folder="templates")

	# Configuration
	# SECRET_KEY обязателен для production - должен быть установлен через переменную окружения
	secret_key = os.environ.get("SECRET_KEY")
	if not secret_key:
		if os.environ.get("FLASK_ENV") == "production":
			raise ValueError("SECRET_KEY must be set in production environment")
		secret_key = "dev-secret-key-change-me"
	app.config["SECRET_KEY"] = secret_key
	
	database_url = os.environ.get("DATABASE_URL")
	if not database_url:
		# Default to SQLite - можно использовать как для разработки, так и для production
		# Для production убедитесь, что файл БД находится в безопасной директории
		# и имеет правильные права доступа (chmod 644)
		database_url = "sqlite:///student_rating.db"
	app.config["SQLALCHEMY_DATABASE_URI"] = database_url
	# SQLite-specific settings
	if database_url.startswith("sqlite"):
		app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
			"connect_args": {"check_same_thread": False}  # Для SQLite в production
		}
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
	
	# Production settings
	app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
	app.config["TESTING"] = False

	# Extensions init
	db.init_app(app)
	migrate.init_app(app, db)
	login_manager.init_app(app)

	# Import models so Alembic sees them
	from . import models  # noqa: F401

	# Blueprints
	from .routes_public import public_bp
	from .routes_admin import admin_bp
	app.register_blueprint(public_bp)
	app.register_blueprint(admin_bp, url_prefix="/admin")

	# Initialize database tables if they don't exist
	with app.app_context():
		try:
			# Check if tables exist by trying to query alembic_version
			from sqlalchemy import inspect
			inspector = inspect(db.engine)
			tables = inspector.get_table_names()
			
			# If no tables exist, create them
			if not tables:
				db.create_all()
		except Exception as e:
			# If inspection fails, try to create tables anyway
			try:
				db.create_all()
			except Exception:
				# If that also fails, log but don't crash
				import logging
				logging.warning(f"Database initialization warning: {e}")

	return app


app = create_app()

