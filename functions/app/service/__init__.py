from flask import Blueprint

service_bp = Blueprint('service', __name__)

from . import tts, tsl, extract, book
