from app import db

class Commande(db.Model):
    __tablename__ = 'commandes'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    total = db.Column(db.Float, nullable=False)
    stripe_session_id = db.Column(db.String)
    statut = db.Column(db.String, default='pending')
    id_client = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    produits = db.relationship('CommandeProduit', backref='commande', lazy=True)

class CommandeProduit(db.Model):
    __tablename__ = 'commandes_produits'

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'), nullable=False)
    produit_id = db.Column(db.Integer, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
