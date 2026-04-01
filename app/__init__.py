from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
import os


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

ALLOWED_EXTENSIONS = {'pdf'}


def create_app():
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[env])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth
    from app.blueprints.admin import admin
    from app.blueprints.customer import customer
    from app.blueprints.professional import professional
    from app.blueprints.main import main

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(customer)
    app.register_blueprint(professional)
    app.register_blueprint(main)

    return app


# app.config['RESUME_FOLDER'] = os.path.join(app.root_path, 'static', 'resume')
