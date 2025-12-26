from app import db


class Vin(db.Model):
    __tablename__ = 'vin'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)

    domaine_id = db.Column(db.Integer, db.ForeignKey('domaine.id'), nullable=False)

    annee = db.Column(db.Integer, nullable=True)

    couleur = db.Column(db.String(50), nullable=False) # Blanc, Rosé, Rouge, Orange, Bleu
    
    prix = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)

    photo = db.Column(db.String(200), nullable=True)

    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Vin {self.nom} ({self.annee})>"
