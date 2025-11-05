from app import db
from datetime import datetime

class PanierSauvegarde(db.Model):
    __tablename__ = 'paniers_sauvegardes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    contenu_json = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PanierSauvegarde {self.id} - user {self.user_id}>'
