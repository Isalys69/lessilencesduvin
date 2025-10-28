import stripe, os
from flask import Blueprint, render_template, request, jsonify, session
from app.utils.panier_tools import get_session_panier
from datetime import datetime
from app import db
from app.models.commandes import Commande, CommandeProduit
from flask_login import current_user


print("Clé publique:", os.getenv("STRIPE_PUBLIC_KEY")[:15], "...")
print("Webhook secret:", os.getenv("STRIPE_WEBHOOK_SECRET")[:15], "...")


paiement_bp = Blueprint('paiement', __name__, url_prefix='/paiement')

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")



@paiement_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    panier = get_session_panier()
    total = sum(i['prix'] * i['qty'] for i in panier)
    montant_cents = int(float(total) * 100)

    # Détection automatique : local ou production
    if request.host.startswith("127.0.0.1") or "localhost" in request.host:
        base_url = "http://127.0.0.1:5000"
    else:
        base_url = "https://www.lessilencesduvin.fr"

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": "Les Silences du Vin"},
                "unit_amount": montant_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{base_url}/paiement/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base_url}/paiement/cancel",
    )
    return jsonify({"id": session.id})


@paiement_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():

    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except stripe.error.SignatureVerificationError:
        return "Signature invalide", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("✅ Paiement confirmé Stripe :", session['id'])
        # ici tu pourrais mettre à jour ta commande dans la base

    return '', 200


# Route affichée après paiement validé
@paiement_bp.route('/success')
def success():
    panier = get_session_panier()
    total = sum(i['prix'] * i['qty'] for i in panier)

    # Récupération du client connecté si existant
    id_client = current_user.user_id if current_user.is_authenticated else None

    # Création de la commande
    commande = Commande(
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=total,
        stripe_session_id=request.args.get('session_id', ''),
        statut='paid',
        id_client=id_client
    )
    db.session.add(commande)
    db.session.flush()  # pour obtenir commande.id avant commit

    # Ajout des produits associés
    print("Panier debug:", panier)

    for item in panier:
        ligne = CommandeProduit(
            commande_id=commande.id,
            produit_id=item['vin_id'],
            quantite=item['qty'],
            prix_unitaire=item['prix']
        )
        db.session.add(ligne)

    db.session.commit()

    print(f"Commande {commande.id} sauvegardée avec succès ✅")

    # Vider le panier
    session.pop('panier', None)

    return render_template('paiement/success.html')

# Route affichée si paiement annulé
@paiement_bp.route('/cancel')
def cancel():
    return render_template('paiement/cancel.html')
