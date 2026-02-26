from app import db
from datetime import datetime

class Commande(db.Model):



    __tablename__ = 'commandes'

    id = db.Column(db.Integer, primary_key=True)

    # Identifiant utilisateur (optionnel)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    # Données du client (toujours requises même si non connecté)
    email_client = db.Column(db.String(120), nullable=True)
    prenom_client = db.Column(db.String(80), nullable=True)
    nom_client = db.Column(db.String(80), nullable=True)

    # Adresse de livraison (requise)
    adresse_livraison = db.Column(db.String(255), nullable=True)
    code_postal_livraison = db.Column(db.String(20), nullable=True)
    ville_livraison = db.Column(db.String(80), nullable=True)
    telephone_livraison = db.Column(db.String(30))

    # Adresse de facturation (facultative)
    adresse_facturation = db.Column(db.String(255))
    code_postal_facturation = db.Column(db.String(20))
    ville_facturation = db.Column(db.String(80))

    # Infos de commande
    total_ttc = db.Column(db.Float, nullable=True)
    devise = db.Column(db.String(3), default='EUR')
    stripe_session_id = db.Column(db.String)

    # Stripe / idempotence
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True, index=True)

    # Refund idempotent (anti double remboursement)
    refund_effectue = db.Column(db.Boolean, default=False, nullable=False)
    stripe_refund_id = db.Column(db.String(255), nullable=True, index=True)
    date_refund = db.Column(db.DateTime, nullable=True)
    
    statut = db.Column(db.String(50), default='en_attente')
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers les produits
    produits = db.relationship('CommandeProduit', backref='commande', lazy=True)

class CommandeProduit(db.Model):
    __tablename__ = 'commandes_produits'

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commandes.id'), nullable=False)
    produit_id = db.Column(db.Integer, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)





