# routes.py – Déclaration des routes principales

from flask import render_template, redirect, url_for, session, request, flash
from app import app
from datetime import datetime
from app import select_locale
from app.translations import get_translations

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
