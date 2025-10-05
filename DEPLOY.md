# DEPLOY.md – G1R0C1
## 🎯 Objectif
Mise en place du déploiement Git ↔ PythonAnywhere pour "Les Silences du Vin"  
But : fluidifier les mises à jour sans transfert manuel de fichiers.

---

## 🔐 1. Génération et ajout de la clé SSH

```bash
ssh-keygen -t ed25519 -C "isalys.creuzeau@gmail.com"
cat ~/.ssh/id_ed25519.pub
