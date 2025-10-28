from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Méthode pour définir le hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Méthode pour vérifier le mot de passe
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Permet à Flask-Login d'utiliser user_id au lieu de id."""
        return str(self.user_id)

# Fonction obligatoire pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
