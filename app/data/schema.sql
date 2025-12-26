CREATE TABLE vins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    millesime INTEGER,
    prix REAL,
    accord TEXT
, domaine varchar(50), image varchar(255), couleur TEXT, description TEXT, selection TEXT DEFAULT 'perso');
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
date DATE,
total REAL,
statut TEXT,
client_id INT);
CREATE TABLE order_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INT,
    vin_id INT,
    qty INT,
    unit_price REAL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(vin_id) REFERENCES vins(id)
);
CREATE TABLE users (
	user_id INTEGER NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (user_id), 
	UNIQUE (email)
);
CREATE TABLE commandes_produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commande_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL,
    prix_unitaire REAL NOT NULL,
    FOREIGN KEY (commande_id) REFERENCES commandes (id)
);
CREATE TABLE commandes (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	email_client VARCHAR(120), 
	prenom_client VARCHAR(80), 
	nom_client VARCHAR(80), 
	adresse_livraison VARCHAR(255), 
	code_postal_livraison VARCHAR(20), 
	ville_livraison VARCHAR(80), 
	telephone_livraison VARCHAR(30), 
	adresse_facturation VARCHAR(255), 
	code_postal_facturation VARCHAR(20), 
	ville_facturation VARCHAR(80), 
	total_ttc FLOAT, 
	devise VARCHAR(3), 
	stripe_session_id VARCHAR, 
	statut VARCHAR(50), 
	date_commande DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);
CREATE TABLE paniers_sauvegardes (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    contenu_json TEXT NOT NULL,
    date_creation DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE domaine (
	id INTEGER NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE vin (
	id INTEGER NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	domaine_id INTEGER NOT NULL, 
	annee INTEGER, 
	couleur VARCHAR(50), 
	prix FLOAT NOT NULL, 
	stock INTEGER NOT NULL, 
	photo VARCHAR(200), 
	description TEXT, typologie VARCHAR(50), 
	PRIMARY KEY (id), 
	FOREIGN KEY(domaine_id) REFERENCES domaine (id)
);
