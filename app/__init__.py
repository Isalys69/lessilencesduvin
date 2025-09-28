import sqlite3
from flask import Flask, g
from pathlib import Path

def get_db():
    if "db" not in g:
        db_path = Path("instance/vins.db")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "s7Df@9z!j2Lp%YqT0vWx3eKuR6BnMh"  # ✅ ajoute la clé ici
    app.teardown_appcontext(close_db)

    # Import et enregistrement du blueprint
    from . import routes
    app.register_blueprint(routes.bp)

    return app
