import os
import sqlite3
from flask import Flask, g
from dotenv import load_dotenv

# Charger les variables d'environnement depuis config/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))

# Crée l'application Flask
app = Flask(__name__, instance_relative_config=True)

# Clé secrète depuis le .env
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Gestion de la base de données SQLite
DATABASE = os.path.join(os.path.dirname(__file__), "..", "vins.db")

def get_db():
    """Retourne la connexion à la base SQLite, attachée au contexte Flask."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    """Ferme la connexion SQLite à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

# Import et enregistrement des routes (via un blueprint)
from app import routes
app.register_blueprint(routes.bp)
