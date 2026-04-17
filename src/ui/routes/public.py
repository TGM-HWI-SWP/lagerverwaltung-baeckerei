import os
import json
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash

from ...ui.shared import service as _service

public_bp = Blueprint("public", __name__)


def _init_demo_data():
    if not _service.get_all_products():
        # Versuche, dummy_data.json zu laden
        # Pfad relativ zum Projektroot berechnen
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[3]  # src/ui/routes/public.py -> 3x parent = project root
        dummy_data_path = project_root / "tests" / "dummy_data.json"
        
        print(f"[DEBUG] Projekt-Root: {project_root}")
        print(f"[DEBUG] Versuche JSON zu laden von: {dummy_data_path}")
        print(f"[DEBUG] Datei existiert: {dummy_data_path.exists()}")
        
        try:
            with open(dummy_data_path, "r", encoding="utf-8") as f:
                products_data = json.load(f)
                print(f"[DEBUG] {len(products_data)} Produkte aus JSON geladen")
                for product in products_data:
                    _service.create_product(
                        product_id=product["id"],
                        name=product["name"],
                        description=product["description"],
                        price=product["price"],
                        category=product.get("category", ""),
                        initial_quantity=product.get("quantity", 0),
                    )
                print("[DEBUG] JSON-Produkte erfolgreich geladen!")
        except Exception as e:
            print(f"[DEBUG] Fehler beim JSON-Laden: {type(e).__name__}: {e}")
            print("[DEBUG] Nutze Fallback-Demo-Daten")

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

        # Füge Demo-Bewegungen hinzu
        print("[DEBUG] Erstelle Demo-Bewegungen...")
        try:
            # Einlagerungen für vorhandene Produkte
            products = _service.get_all_products()
            for product_id, product in products.items():
                if product.quantity > 0:
                    _service.add_to_stock(product_id, product.quantity, "Initiale Einlagerung", "System")
            
            # Zusätzliche Bewegungen für Nachvollziehbarkeit
            if "BR001" in products:
                _service.remove_from_stock("BR001", 5, "Verkauf an Kunden", "Anna Schmidt")
                _service.add_to_stock("BR001", 10, "Nachlieferung", "Max Müller")
            
            print("[DEBUG] Demo-Bewegungen erfolgreich erstellt!")
        except Exception as e:
            print(f"[DEBUG] Fehler bei Demo-Bewegungen: {e}")


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
