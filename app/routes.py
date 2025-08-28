# routes.py – Déclaration des routes principales

from flask import render_template, redirect, url_for, session, request, flash
from flask import jsonify, abort, current_app

from app import app
from datetime import datetime
from app import select_locale
from app.translations import get_translations
from dotenv import load_dotenv

import os
import stripe

#bp = Blueprint('paiement', __name__)
# Charger le fichier .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "config", ".env"))

# Clés Stripe via variables d'environnement
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")


# Route d'accueil principale
@app.route("/")
def home():
    return render_template('index.html')

# Route entrée boutique
@app.route("/shopenter")
def shopenter():
    return render_template('shopenter.html')

# Route du panier
@app.route("/shoppingbasket")
def shoppingbasket():
    return render_template('shoppingbasket.html')

# Route vers le paiement
@app.route("/payment")
def payment():
    return render_template('payment.html')


# Route d'identification client connu
@app.route("/signup", methods=["POST"])
def signup():
    # ...traitement des données, enregistrement en base...
    # Redirection obligatoire vers agegate pour validation de majorité
    return redirect(url_for("agegate"))


# Route : vérification d'âge
@app.route('/agegate', methods=['GET', 'POST'])
def agegate():
    # 1. Récupère la langue dans l’URL, fallback français
    lang = request.args.get('lang', 'fr')
    t = get_translations(lang)  # dictionnaire de traduction dans la langue voulue
    message = None

    # 2. Si le formulaire est soumis
    if request.method == 'POST':
        birthdate_str = request.form.get('birthdate')
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
            today = datetime.today()
            age = (today - birthdate).days // 365
            if age >= 18:
                session['is_adult'] = True
                # On garde la langue sélectionnée dans l’URL lors du redirect
                return redirect(url_for('home', lang=lang))
            else:
                # Message d’erreur spécifique si mineur
                message = t["error_minor"]
        except Exception:
            # Message d’erreur si saisie invalide
            message = t["error_invalid"]

    # 3. Affiche la page, en transmettant toutes les variables utiles au template
    return render_template(
        "agegate.html",  # Le template à afficher
        t=t,             # Le dictionnaire de traductions
        lang=lang,       # Le code langue courant (pour l’attribut <html lang="...">)
        message=message  # Un éventuel message d’erreur (sinon None)
    )

# Route d’authentification globale : connexion ET création de compte
@app.route("/auth", methods=["GET", "POST"])
def authentication():
    # Pour l’instant, on ne gère pas encore la logique de traitement,
    # on se concentre sur l’affichage du formulaire.
    return render_template("authentication.html")


@app.route("/confidentialite")
def confidentialite():
    return render_template("confidentialite.html")

@app.route("/mentions-legales")
def mentions_legales():
    return render_template("mentions_legales.html")

@app.route("/cgv")
def cgv():
    return render_template("cgv.html")


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    # Garde-fou minimal
    if not stripe.api_key or not stripe.api_key.startswith("sk_"):
        return jsonify({"error": "Stripe non configuré"}), 500

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            success_url = url_for("success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url  = url_for("cancel",  _external=True),
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": "Commande Les Silences du Vin"},
                    "unit_amount": 2000  # 20,00 € (en centimes)
                },
                "quantity": 1
            }],
        )
        return jsonify({"url": session.url}), 200

    except Exception as e:
        current_app.logger.exception("Erreur Stripe Checkout")
        return jsonify({"error": str(e)}), 400


@app.route("/paiement/success")
def success():
    session_id = request.args.get("session_id")
    if not session_id:
        abort(400, "session_id manquant")

    s = stripe.checkout.Session.retrieve(session_id)
    if s.payment_status == "paid":
        current_app.logger.info(f"PAIEMENT OK session={s.id} total={s.amount_total}{s.currency}")
        return render_template("success.html", title="Paiement réussi", session=s)

    return render_template("cancel.html", title="Paiement non confirmé"), 400


@app.route("/paiement/cancel")
def cancel():
    return render_template("cancel.html", title="Paiement annulé")

