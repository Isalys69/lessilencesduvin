CREATE TABLE vins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    millesime INTEGER,
    prix REAL,
    accord TEXT
, domaine varchar(50), image varchar(255));
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
