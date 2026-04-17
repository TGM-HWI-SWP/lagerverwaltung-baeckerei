import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from ...ui.shared import service as _service

admin_bp = Blueprint("admin", __name__)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def _is_logged_in():
    return session.get("admin_logged_in", False)


def _login_required(view_func):
    def wrapper(*args, **kwargs):
        if not _is_logged_in():
            flash("Bitte melden Sie sich zuerst an.", "warning")
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return wrapper


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Erfolgreich angemeldet", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Ungültige Admin-Zugangsdaten", "danger")

    return render_template("admin_login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("Abgemeldet", "info")
    return redirect(url_for("public.home"))


@admin_bp.route("/dashboard")
@_login_required
def dashboard():
    total_products = len(_service.get_all_products())
    total_stock_value = _service.get_total_inventory_value()
    total_orders = len(_service.get_movements())

    return render_template(
        "admin_dashboard.html",
        total_products=total_products,
        total_stock_value=total_stock_value,
        total_orders=total_orders,
    )


@admin_bp.route("/orders")
@_login_required
def orders():
    movements = _service.get_movements()
    return render_template("admin_orders.html", movements=movements)


@admin_bp.route("/inventory")
@_login_required
def inventory():
    products = _service.get_all_products()
    return render_template("admin_inventory.html", products=products)


@admin_bp.route("/statistics")
@_login_required
def statistics():
    products = _service.get_all_products().values()
    total_units = sum(p.quantity for p in products)
    total_value = _service.get_total_inventory_value()

    return render_template("admin_statistics.html", total_units=total_units, total_value=total_value)


@admin_bp.route("/movements")
@_login_required
def movements():
    # Hole alle Bewegungen
    all_movements = _service.get_movements()
    print(f"[DEBUG] Anzahl Bewegungen im Repository: {len(all_movements)}")
    for m in all_movements:
        print(f"[DEBUG] Bewegung: {m.product_name} | {m.movement_type} | {m.quantity_change}")
    
    # Hole Movement Report pro Produkt (aus Warehouse)
    movement_report = _service.warehouse.get_movement_report()
    print(f"[DEBUG] Movement Report Keys: {list(movement_report.keys())}")
    
    # Gesamtstatistiken
    movement_stats = _service.warehouse.get_movement_statistics()
    print(f"[DEBUG] Movement Stats: {movement_stats}")
    
    return render_template(
        "admin_movements.html",
        all_movements=all_movements,
        movement_report=movement_report,
        movement_stats=movement_stats
    )
