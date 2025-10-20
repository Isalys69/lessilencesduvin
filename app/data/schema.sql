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
	id INTEGER NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
