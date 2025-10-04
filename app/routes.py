from flask import Blueprint, render_template

bp = Blueprint("routes", __name__)

@bp.route("/")
def construction():
    return render_template("construction.html")


@bp.route("/catalogue")
def catalogue():
    return render_template("catalogue.html")

@bp.route("/rouge")
def rouge():
    return render_template("rouge.html")

@bp.route("/blanc")
def blanc():
    return render_template("blanc.html")

@bp.route("/garde")
def garde():
    return render_template("garde.html")

@bp.route("/contact")
def contact():
    return render_template("contact.html")


