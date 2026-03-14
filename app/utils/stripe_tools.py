import stripe
from datetime import datetime
from flask import current_app
from app.extensions import db


# Transitions autorisées par statut
TRANSITIONS_ADMIN = {
    "payé":           ["annulée"],                    # adresse manquante → annulation seulement
    "complétée":      ["en_préparation", "annulée"],  # adresse reçue → peut traiter
    "en_préparation": ["expédiée",       "annulée"],
    "expédiée":       ["livrée"],
}

# Libellés affichés dans les boutons
LABELS_STATUT = {
    "en_préparation": ("primary",   "bi-box-seam",       "En préparation"),
    "expédiée":       ("success",   "bi-truck",          "Expédiée"),
    "livrée":         ("dark",      "bi-check2-circle",  "Livrée"),
    "annulée":        ("danger",    "bi-x-circle",       "Annuler & rembourser"),
}


def safe_refund(commande):
    """Rembourse via Stripe si payment_intent existe et remboursement pas encore effectué.
    Retourne (True, refund_id) en cas de succès, (False, message_erreur) sinon."""
    if not commande.stripe_payment_intent_id:
        return False, "Aucun payment_intent Stripe associé à cette commande."

    if commande.refund_effectue:
        return True, commande.stripe_refund_id  # idempotent

    try:
        refund = stripe.Refund.create(payment_intent=commande.stripe_payment_intent_id)
        commande.refund_effectue = True
        commande.stripe_refund_id = refund.get("id")
        commande.date_refund = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(
            f"[REFUND] Commande {commande.id} remboursée refund_id={commande.stripe_refund_id}"
        )
        return True, commande.stripe_refund_id
    except Exception as e:
        current_app.logger.error(
            f"[REFUND] Échec remboursement commande {commande.id}: {type(e).__name__} - {e}"
        )
        return False, str(e)
