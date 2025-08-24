import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY") or "lesilencesduvin-dev-key"

# Configuration minimale d'une base SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'lesilencesduvin.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
