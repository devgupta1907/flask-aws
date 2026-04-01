from flask import Blueprint

professional = Blueprint('professional', __name__)

from app.blueprints.professional import routes