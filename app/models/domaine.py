from app import db

class Domaine(db.Model):
    __tablename__ = 'domaine'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)

    # Relation vers Vin (ne crée rien en BDD, juste pratique)
    vins = db.relationship('Vin', backref='domaine', lazy=True)

    def __repr__(self):
        return f"<Domaine {self.nom}>"
