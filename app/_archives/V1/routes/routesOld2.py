from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from pathlib import Path

bp = Blueprint("routes", __name__)

# Helper pour initialiser le panier
def _init_cart():
    if "cart" not in session:
        session["cart"] = {}
        session.modified = True

@bp.route("/")
def construction():
    return render_template("construction.html")


@bp.route("/catalogue")
def catalogue():
    db_path = Path("instance/vins.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    vins = conn.execute("SELECT * FROM vins").fetchall()
    conn.close()
    return render_template("catalogue.html", vins=vins)


@bp.route('/shoppingbasket', methods=['GET', 'POST'])
def shoppingbasket():
    db_path = Path("instance/vins.db")
    _init_cart()

    if request.method == "POST":
        vin_id = request.form.get("vin_id")
        if vin_id:
            cart = session["cart"]
            cart[vin_id] = cart.get(vin_id, 0) + 1
            session["cart"] = cart
            session.modified = True
        return redirect(url_for("routes.shoppingbasket"))

    # --- GET : Reconstituer le panier ---
    cart = session.get("cart", {})
    items = []
    total = 0.0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for vin_id_str, qty in cart.items():
        cursor.execute("SELECT id, nom, prix FROM vins WHERE id = ?", (vin_id_str,))
        row = cursor.fetchone()
        if row:
            vin_id, nom, prix = row
            line_total = prix * qty
            items.append({
                "id": vin_id,
                "nom": nom,
                "prix": prix,
                "qty": qty,
                "line_total": line_total
            })
            total += line_total

    conn.close()

    return render_template("shoppingbasket.html", items=items, total=total)


@bp.route("/update_cart", methods=["POST"])
def update_cart():
    vin_id = request.form.get("vin_id")
    action = request.form.get("action")

    cart = session.get("cart", {})

    if vin_id:
        if action == "remove":
            cart.pop(vin_id, None)
        elif action == "increase":
            cart[vin_id] = cart.get(vin_id, 0) + 1
        elif action == "decrease":
            if cart.get(vin_id, 0) <= 1:
                cart.pop(vin_id, None)
            else:
                cart[vin_id] -= 1

        session["cart"] = cart
        session.modified = True

    return redirect(url_for("routes.shoppingbasket"))

@bp.route('/shopenter', methods=['GET', 'POST'])
def shopenter():
    return render_template("shopenter.html")


@bp.route("/checkout", methods=["POST"])
def checkout():
    db_path = Path("instance/vins.db")
    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("routes.shoppingbasket"))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1) Reconstituer le panier depuis la session
    items = []
    total = 0.0
    for vin_id, qty in cart.items():
        cursor.execute("SELECT id, nom, prix FROM vins WHERE id=?", (vin_id,))
        row = cursor.fetchone()
        if row:
            vin_id, nom, prix = row
            line_total = prix * qty
            items.append({
                "id": vin_id,
                "nom": nom,
                "prix": prix,
                "qty": qty,
                "line_total": line_total
            })
            total += line_total

    # 2) Créer une commande dans "orders"
    cursor.execute(
        "INSERT INTO orders (date, total, statut, client_id) VALUES (DATE('now'), ?, 'En attente', NULL)",
        (total,)
    )
    order_id = cursor.lastrowid

    # 3) Créer les lignes de commande dans "order_lines"
    for line in items:
        cursor.execute(
            "INSERT INTO order_lines (order_id, vin_id, qty, unit_price) VALUES (?, ?, ?, ?)",
            (order_id, line["id"], line["qty"], line["prix"])
        )

    conn.commit()

    # 4) Charger la commande + lignes pour affichage
    cursor.execute("SELECT id, date, total, statut FROM orders WHERE id=?", (order_id,))
    order_row = cursor.fetchone()
    order = {
        "id": order_row[0],
        "date": order_row[1],
        "total": order_row[2],
        "statut": order_row[3]
    }

    cursor.execute("""
        SELECT v.nom, ol.qty, ol.unit_price
        FROM order_lines ol
        JOIN vins v ON ol.vin_id = v.id
        WHERE ol.order_id=?
    """, (order_id,))
    order_lines = [{"nom": r[0], "qty": r[1], "unit_price": r[2]} for r in cursor.fetchall()]

    conn.close()

    # 5) Vider le panier
    session["cart"] = {}
    session.modified = True

    # 6) Afficher la page de confirmation
    return render_template("checkout.html", order=order, order_lines=order_lines)


