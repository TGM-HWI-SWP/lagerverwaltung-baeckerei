import os
from flask import Blueprint, render_template, request, redirect, url_for, flash

from ...adapters.repository import RepositoryFactory
from ...services import WarehouseService

public_bp = Blueprint("public", __name__)

# Service-Layer-Anbindung (dynamisch, per ENV, fallback InMemory)
repository_type = os.getenv("REPOSITORY_TYPE", "memory")
_repository = RepositoryFactory.create_repository(repository_type)
_service = WarehouseService(_repository)


def _init_demo_data():
    if not _service.get_all_products():
        _service.create_product(
            product_id="BROT-001",
            name="Kartoffelbrot",
            description="Frisches Roggen-Kartoffel-Brot",
            price=4.50,
            category="Brot",
            initial_quantity=50,
        )
        _service.create_product(
            product_id="BREZEL-001",
            name="Laugenbrezel",
            description="Knusprige Brezel mit Körnern",
            price=2.20,
            category="Backwaren",
            initial_quantity=80,
        )
        _service.create_product(
            product_id="KUCHEN-001",
            name="Apfelkuchen",
            description="Hausgemachter Apfelkuchen (Stück)",
            price=3.80,
            category="Kuchen",
            initial_quantity=25,
        )


_init_demo_data()


@public_bp.route("/")
def home():
    return render_template("home.html")


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/products")
def product_list():
    products = _service.get_all_products()
    return render_template("product_list.html", products=products)


@public_bp.route("/product/<product_id>")
def product_detail(product_id):
    product = _service.get_product(product_id)
    if not product:
        flash("Produkt nicht gefunden", "warning")
        return redirect(url_for("public.product_list"))

    return render_template("product_detail.html", product=product)


@public_bp.route("/order", methods=["GET", "POST"])
def order():
    products = _service.get_all_products()
    order_date = None
    message = None

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity = int(request.form.get("quantity", 1))

        try:
            _service.remove_from_stock(product_id, quantity, reason="Online-Bestellung", user="customer")
            message = f"Bestellung erfolgreich: {quantity}x {product_id}."
        except Exception as err:
            message = f"Bestellung fehlgeschlagen: {err}"

    return render_template("order.html", products=products, message=message)
