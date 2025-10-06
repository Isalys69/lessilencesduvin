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

