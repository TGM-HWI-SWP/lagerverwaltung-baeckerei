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
                        image=product.get("image"),
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


from datetime import datetime, timedelta


def _get_min_date():
    """Gibt das frühestmögliche Datum zurück (heute + 1 Tag)."""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def _build_cart(products, selected_products, quantities_dict):
    """Baut den Warenkorb aus den Formulardaten."""
    cart = []
    for product_id in selected_products:
        if product_id in products:
            qty_key = f"quantity_{product_id}"
            qty = int(quantities_dict.get(qty_key, 1))
            if qty > 0:
                cart.append({"product_id": product_id, "quantity": qty})
    return cart


def _calculate_cart_total(cart, products):
    """Berechnet die Gesamtsumme des Warenkorbs."""
    total = 0
    for item in cart:
        if item["product_id"] in products:
            total += products[item["product_id"]].price * item["quantity"]
    return total


@public_bp.route("/order", methods=["GET", "POST"])
def order():
    products = _service.get_all_products()
    message = None
    step = request.form.get("step", "") if request.method == "POST" else ""
    validation_errors = []
    
    # Formulardaten für Wiederverwendung bei Fehlern
    customer_name = request.form.get("customer_name", "")
    customer_email = request.form.get("customer_email", "")
    pickup_date = request.form.get("pickup_date", "")
    pickup_time = request.form.get("pickup_time", "")
    
    # Warenkorb aus Formular oder Session
    selected_products = request.form.getlist("selected_products")
    quantities_dict = {k: v for k, v in request.form.items() if k.startswith("quantity_")}
    cart = _build_cart(products, selected_products, quantities_dict)
    cart_total = _calculate_cart_total(cart, products)
    
    # IDs der Produkte im Warenkorb für Template
    cart_product_ids = [item["product_id"] for item in cart]
    cart_quantities = {item["product_id"]: item["quantity"] for item in cart}
    
    # Template-Daten vorbereiten
    template_data = {
        "products": products,
        "message": message,
        "step": step,
        "validation_errors": validation_errors,
        "cart": cart,
        "cart_total": cart_total,
        "cart_product_ids": cart_product_ids,
        "cart_quantities": cart_quantities,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "pickup_date": pickup_date,
        "pickup_time": pickup_time,
        "min_date": _get_min_date(),
    }

    if request.method == "POST":
        # Schritt: Warenkorb aktualisieren
        if step == "cart":
            return render_template("order.html", **template_data)
        
        # Schritt: Kundendaten eingeben (validieren)
        elif step == "customer":
            if not cart:
                validation_errors.append("Bitte wählen Sie mindestens ein Produkt aus.")
            
            if not customer_name:
                validation_errors.append("Bitte geben Sie Ihren Namen ein.")
            elif len(customer_name) < 2:
                validation_errors.append("Der Name muss mindestens 2 Zeichen lang sein.")
            
            if not customer_email:
                validation_errors.append("Bitte geben Sie Ihre E-Mail-Adresse ein.")
            elif "@" not in customer_email or "." not in customer_email.split("@")[-1]:
                validation_errors.append("Bitte geben Sie eine gültige E-Mail-Adresse ein.")
            
            if not pickup_date:
                validation_errors.append("Bitte wählen Sie ein Datum für die Abholung.")
            else:
                try:
                    selected_date = datetime.strptime(pickup_date, "%Y-%m-%d")
                    min_date = datetime.strptime(_get_min_date(), "%Y-%m-%d")
                    if selected_date < min_date:
                        validation_errors.append("Das Abholdatum muss mindestens ein Tag in der Zukunft liegen.")
                except ValueError:
                    validation_errors.append("Ungültiges Datum.")
            
            if not pickup_time:
                validation_errors.append("Bitte wählen Sie eine Uhrzeit für die Abholung.")
            
            if not validation_errors:
                step = "summary"
                template_data["step"] = step
                return render_template("order.html", **template_data)
            else:
                template_data["validation_errors"] = validation_errors
                return render_template("order.html", **template_data)
        
        # Bestellung finalisieren
        elif request.form.get("confirm") == "1":
            product_ids = request.form.getlist("product_ids")
            quantities = request.form.getlist("quantities")
            customer_name = request.form.get("customer_name")
            customer_email = request.form.get("customer_email")
            pickup_date = request.form.get("pickup_date")
            pickup_time = request.form.get("pickup_time")
            
            # Warenkorb neu bauen aus hidden fields
            cart = []
            for pid, qty in zip(product_ids, quantities):
                cart.append({"product_id": pid, "quantity": int(qty)})
            
            # Lagerbestand prüfen und abbuchen
            try:
                for item in cart:
                    product = products.get(item["product_id"])
                    if not product:
                        raise Exception(f"Produkt {item['product_id']} nicht gefunden.")
                    if product.quantity < item["quantity"]:
                        raise Exception(f"Nicht genügend Lagerbestand für {product.name}. Verfügbar: {product.quantity}")
                    
                    _service.remove_from_stock(
                        item["product_id"], 
                        item["quantity"], 
                        reason=f"Online-Bestellung: Abholung {pickup_date} um {pickup_time}", 
                        user=customer_name
                    )
                
                # Produktliste für Bestellbestätigung
                product_list = ", ".join([f"{products[item['product_id']].name} ({item['quantity']}x)" for item in cart])
                message = f"Bestellung erfolgreich! Sie erhalten eine Bestellbestätigung an {customer_email}. Ihre Bestellung: {product_list}. Bitte holen Sie Ihre Bestellung am {pickup_date} um {pickup_time} Uhr ab."
                flash(message, "success")
                return redirect(url_for("public.order"))
            except Exception as err:
                message = f"Bestellung fehlgeschlagen: {err}"
                flash(message, "error")
                template_data["message"] = message
                return render_template("order.html", **template_data)
        
        # Erster Schritt: Warenkorb (falls POST aber kein step)
        else:
            return render_template("order.html", **template_data)

    return render_template("order.html", **template_data)
