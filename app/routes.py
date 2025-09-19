from flask import Blueprint, render_template
import sqlite3
from pathlib import Path

bp = Blueprint("routes", __name__)

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
    return render_template("shoppingbasket.html")


@bp.route('/shopenter', methods=['GET', 'POST'])
def shopenter():
    return render_template("shopenter.html")
