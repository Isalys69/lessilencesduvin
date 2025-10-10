# DEPLOY.md – G1R0C1
## 🎯 Objectif
Mise en place du déploiement Git ↔ PythonAnywhere pour "Les Silences du Vin"  
But : fluidifier les mises à jour sans transfert manuel de fichiers.

---

## 🔐 1. Génération et ajout de la clé SSH

```bash
ssh-keygen -t ed25519 -C "isalys.creuzeau@gmail.com"
cat ~/.ssh/id_ed25519.pub


## Notes version G1R0C3 – Refonte Flask avec Blueprints
**Objectif :**  
Refonte de la structure Flask en architecture modulaire avec Blueprints.  
Chaque fichier `routes.py` agit désormais comme un **conteneur de routes** pour son module.

**Principaux changements :**
- Suppression du fichier monolithique `app/routes.py`
- Création des modules :
  - `main` → page d’accueil `/`
  - `catalogue` → page catalogue `/catalogue/`
  - `contact` → page contact `/contact/`
- Nouvelle fonction `create_app()` dans `app/__init__.py`
- Mise à jour des imports (`from app.routes.<module> import <module>_bp`)
- Tests des endpoints avec :  
  ```bash
  flask --app run routes



## 🧾 G1R0C5 — Pages légales conformes (Mentions, CGV, Confidentialité)

### 🎯 Objectif
Mettre en place les trois pages légales obligatoires (mentions légales, CGV, politique de confidentialité)
dans une architecture Flask modulaire, conforme au RGPD et adaptée à la vente en ligne de vins.

---

### 🧱 Implémentation
- Création du **Blueprint** `legales` :
app/routes/legales/
├── init.py
└── routes.py
- `routes.py` contient les 3 routes :
  - `/legales/mentions`
  - `/legales/cgv`
  - `/legales/confidentialite`
- `__init__.py` réexporte `legales_bp`.

- Ajout des templates correspondants :
app/templates/legales/
├── mentions.html
├── cgv.html
└── confidentialite.html

- Mise à jour du footer dans `base.html` :
```html
<footer>
  <a href="{{ url_for('legales.mentions') }}">Mentions légales</a> |
  <a href="{{ url_for('legales.cgv') }}">CGV</a> |
  <a href="{{ url_for('legales.confidentialite') }}">Confidentialité</a>
  <p>&copy; 2025 Les Silences du Vin</p>
</footer>
⚙️ Déploiement
Suppression de l’ancien fichier d’entrée flask_app.py.
Mise à jour du fichier WSGI :
from app import create_app
application = create_app()
Pull Git réussi :
git pull → Fast-forward ok (6c4116f)
Tests en production :
/legales/mentions → ✅
/legales/cgv → ✅
/legales/confidentialite → ✅
🧹 Nettoyage post-déploiement
Suppression des anciens répertoires racine static/ et templates/
(remplacés par app/static/ et app/templates/).
Vérification : git status → nothing to commit, working tree clean.
📦 Statut
✅ Déployé en production
🕒 07 octobre 2025
🔖 Commit : G1R0C5 — Ajout pages légales conformes (Mentions, CGV, Confidentialité)


## 🏁 G1R1C0 — Cadran 1 (Urgent & Important) clôturé

### 🎯 Objectif
Finaliser le socle technique et légal du projet avant ouverture publique.

### 🧩 Contenu
- Architecture Flask professionnelle (Blueprints + templates)
- Connexion Git ↔ PythonAnywhere
- Nettoyage du dépôt et versionnage clair
- Ajout des pages légales conformes (RGPD + CGV)
- Tests et validation de production

### 🏷️ Tag Git
`G1R1C0` — Stabilisation Flask + déploiement production

### 📦 Statut
✅ Terminé — 07 octobre 2025

🟣 G1R2C1 — Connexion base SQLite & affichage dynamique
Date : 09/10/2025
Auteur : Isalys
Objectif : Passage du site Les Silences du Vin en affichage dynamique à partir d’une base SQLite.
Modifications principales :
Ajout d’un logger avec fichier app/data/app.log
Centralisation des fonctions get_db() et close_db() au niveau du module app
Création du template unique vins_couleur.html pour les pages Rouge / Blanc / Garde
Intégration de Bootstrap 5 (CDN) pour la mise en page responsive
Migration du dossier d’images vers app/static/img/vins/
Vérification du .gitignore (suppression des .DS_Store)
Test des routes dynamiques : /rouge, /blanc, /garde
Import de la base locale vins.db sur PythonAnywhere
Validation du fonctionnement prod après déploiement git pull origin main
Commandes principales :
# Déploiement
cd lessilencesduvin
git pull origin main

# Vérification structure
sqlite3 app/data/vins.db
.tables
SELECT COUNT(*) FROM vins;

# Reload application
[Reload depuis le Dashboard PythonAnywhere]
Résultat :
✅ Connexion SQLite stable
✅ Affichage dynamique des vins validé
✅ Mise en page responsive opérationnelle
✅ Données locales synchronisées avec la prod

🧾 Validation production – G1R2C2
📅 10 octobre 2025
🎯 Objectif
Mise en production du formulaire de contact sécurisé :
Remplacement du mailto: par un envoi réel via SMTP OVH
Gestion du multi-destinataires
Sécurisation par variables d’environnement .env
Intégration Flask-WTF / WTForms (validation et CSRF)
Affichage des messages flash Bootstrap (succès / erreur)
Chargement correct du .env dans l’environnement WSGI
⚙️ Modifications principales
Fichier Contenu
app/forms/contact_form.py Création du formulaire WTForms
app/routes/contact/routes.py  Logique d’envoi SMTP et messages flash
app/config.py Chargement .env + fallback MAIL_RECIPIENT
app/templates/contact.html  Nouveau formulaire Bootstrap
app/templates/base.html Bloc de messages flash
www_lessilencesduvin_fr_wsgi.py Ajout du chargement .env avant create_app()
🧩 Déploiement PythonAnywhere
cd ~/lessilencesduvin
git pull origin main
touch /var/www/lessilencesduvin_pythonanywhere_com_wsgi.py
🧪 Vérifications post-déploiement
 Page /contact accessible
 Envoi du formulaire → contact@lessilencesduvin.fr + contact@inspirecode.fr
 Message flash “Votre message a bien été envoyé” visible
 Aucun log d’erreur WSGI
 .env chargé correctement via WSGI
🏁 Résultat
Version G1R2C2 stable et validée en production.
Prochaine étape : optimisation UX & gestion dynamique des contenus (G1R3).
