from app import db

class Vin(db.Model):
    __tablename__ = "vin"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    domaine_id = db.Column(db.Integer, db.ForeignKey("domaine.id"), nullable=False)
    annee = db.Column(db.Integer)
    couleur = db.Column(db.String(50))
    prix = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    photo = db.Column(db.String(255))
    description = db.Column(db.Text)
    typologie = db.Column(db.String(100))
    accord = db.Column(db.String(255))

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Vin {self.nom} ({self.annee})>"
