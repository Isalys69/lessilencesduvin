from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from pathlib import Path

bp = Blueprint("routes", __name__)

# Helper pour initialiser le panier
def _init_cart():
    if "cart" not in session:
        session["cart"] = {}
        session.modified = True

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

    # --- GET : afficher le panier ---
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

@bp.route('/shopenter', methods=['GET', 'POST'])
def shopenter():
    return render_template("shopenter.html")
