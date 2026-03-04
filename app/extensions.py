# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
# ───────────────────────────────────────────
# 🔐 Protection CSRF (Cross-Site Request Forgery)
# ------------------------------------------------
# Flask-WTF ajoute un jeton CSRF dans chaque formulaire WTForms
# (via {{ form.hidden_tag() }} dans les templates).
#
# CSRFProtect active une vérification globale côté serveur :
# toute requête POST/PUT/PATCH/DELETE doit contenir un token valide,
# sinon Flask renvoie une erreur 400.
#
# Cela empêche un site externe de déclencher des actions à l'insu
# d'un utilisateur authentifié (attaque CSRF).
#
# ⚠️ Certaines routes API doivent être exemptées :
# - webhook Stripe (paiement)
# → utiliser @csrf.exempt sur la route concernée.
# ───────────────────────────────────────────
csrf = CSRFProtect()