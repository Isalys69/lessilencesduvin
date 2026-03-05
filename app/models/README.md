## 🧱 Gestion de la base de données (V3)

À partir de la version **G3R1**, le projet *Les Silences du Vin* repose sur une base SQLite gérée par **SQLAlchemy**, 
remplaçant l’accès direct via `sqlite3`.

### Pourquoi cette évolution
L’intégration de SQLAlchemy apporte :
- une **couche de sécurité** (prévention des injections SQL),
- la **gestion automatique des sessions et transactions**,
- la **compatibilité future** avec d’autres moteurs (PostgreSQL, MySQL…),
- et l’accès à des **fonctionnalités avancées** absentes de `sqlite3` (relations entre tables, ORM, etc.).

### Création des tables
> 🔒 Les tables ne sont **jamais créées automatiquement** au démarrage de Flask.

Elles doivent être **créées manuellement** par l’administrateur à l’aide du shell Flask :

```bash
flask shell
>>> from app.extensions import db, create_app
>>> app = create_app()
>>> app.app_context().push()
>>> db.create_all()
>>> exit()
Cette approche garantit un contrôle total sur la structure et évite toute altération non souhaitée en production.
Modification des tables
Les évolutions de structure (ajout ou suppression de colonnes, changement de type, etc.)
se font pour l’instant de manière artisanale, directement dans SQLite :
sqlite3 app/data/vins.db
sqlite> ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;
Chaque modification est ensuite tracée par export du schéma SQL :
sqlite3 app/data/vins.db .schema > app/data/schema.sql
Commandes et requêtes
Toutes les opérations de lecture, écriture ou suppression
s’effectuent via les modèles SQLAlchemy (ORM) depuis les routes Flask
ou via des scripts manuels pour les tests et la maintenance.
Synthèse
Action	Méthode	Objectif
Création de tables	db.create_all() (manuel)	Structure maîtrisée
Lecture / écriture	ORM SQLAlchemy	Sécurité & simplicité
Modification de tables	SQL direct ou migration future	Souplesse
Export structure	.schema + Git	Traçabilité
🧭 Philosophie : Les Silences du Vin reste un projet artisanal et maîtrisé,
alliant rigueur technique et liberté de création.
