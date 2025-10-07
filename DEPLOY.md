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
