import base64
import io
from datetime import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file

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
    products = list(_service.get_all_products().values())
    total_products = len(products)
    total_units = sum(p.quantity for p in products)
    total_value = _service.get_total_inventory_value()
    average_price = float("%.2f" % (total_value / total_units)) if total_units else 0.0
    average_stock = float("%.2f" % (total_units / total_products)) if total_products else 0.0

    product_reports = [
        {
            "id": p.id,
            "name": p.name,
            "quantity": p.quantity,
            "price": p.price,
            "total_value": p.get_total_value(),
            "category": p.category,
        }
        for p in products
    ]

    categories = {}
    for item in product_reports:
        category = item["category"] or "Unkategorisiert"
        categories[category] = categories.get(category, 0) + 1

    movements = _service.get_movements()
    total_movements = len(movements)
    total_incoming = sum(m.quantity_change for m in movements if m.quantity_change > 0)
    total_outgoing = sum(abs(m.quantity_change) for m in movements if m.quantity_change < 0)
    moved_products = set(m.product_id for m in movements)

    movement_counts = {}
    sales_by_product = {}
    for m in movements:
        movement_counts[m.product_name] = movement_counts.get(m.product_name, 0) + 1
        if m.quantity_change < 0:
            sales_by_product[m.product_name] = sales_by_product.get(m.product_name, 0) + abs(m.quantity_change)

    top_moved_products = sorted(
        [{"name": name, "count": count} for name, count in movement_counts.items()],
        key=lambda item: item["count"],
        reverse=True,
    )[:5]

    top_sold_products = sorted(
        [{"name": name, "sold": sold} for name, sold in sales_by_product.items()],
        key=lambda item: item["sold"],
        reverse=True,
    )[:5]

    top_by_value = sorted(product_reports, key=lambda item: item["total_value"], reverse=True)[:5]
    top_by_quantity = sorted(product_reports, key=lambda item: item["quantity"], reverse=True)[:5]
    low_stock = [item for item in product_reports if item["quantity"] <= 10]

    return render_template(
        "admin_statistics.html",
        total_products=total_products,
        total_units=total_units,
        total_value=total_value,
        average_price=average_price,
        average_stock=average_stock,
        total_movements=total_movements,
        total_incoming=total_incoming,
        total_outgoing=total_outgoing,
        moved_products=len(moved_products),
        product_reports=product_reports,
        categories=categories,
        top_by_value=top_by_value,
        top_by_quantity=top_by_quantity,
        top_moved_products=top_moved_products,
        top_sold_products=top_sold_products,
        low_stock=low_stock,
    )


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


@admin_bp.route("/movements/statistics")
@_login_required
def movement_statistics():
    movements = _service.get_movements()

    # Nur verkaufsrelevante Bewegungen
    sales_movements = [m for m in movements if m.movement_type == "OUT"]

    sales_by_product = {}
    sales_by_product_and_time = {}
    
    for m in sales_movements:
        product_name = m.product_name
        sold_amount = abs(m.quantity_change)
        
        # Gesamtverkäufe pro Produkt
        sales_by_product[product_name] = sales_by_product.get(product_name, 0) + sold_amount
        
        # Verkäufe pro Produkt und Uhrzeit
        if product_name not in sales_by_product_and_time:
            sales_by_product_and_time[product_name] = {}
        
        time_key = m.timestamp.strftime("%H:%M:%S")
        sales_by_product_and_time[product_name][time_key] = (
            sales_by_product_and_time[product_name].get(time_key, 0) + sold_amount
        )

    if not sales_by_product:
        img_data = None
    else:
        plt.switch_backend("Agg")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), constrained_layout=True)

        # Produkte mit den meisten Verkäufen
        product_names = list(sales_by_product.keys())
        sold_values = [sales_by_product[name] for name in product_names]

        colors = [
            "#6c5ce7",
            "#00b894",
            "#fdcb6e",
            "#e17055",
            "#74b9ff",
            "#fd79a8",
            "#55efc4",
            "#ffeaa7",
            "#d63031",
            "#0984e3",
        ]
        product_colors = {
            product: colors[idx % len(colors)]
            for idx, product in enumerate(product_names)
        }

        bar_colors = [product_colors[name] for name in product_names]
        ax1.bar(product_names, sold_values, color=bar_colors)
        ax1.set_title("Am meisten gekaufte Produkte")
        ax1.set_ylabel("Menge verkauft")
        ax1.set_xlabel("Produkt")
        ax1.tick_params(axis="x", rotation=45)

        # Verkauf pro Produkt und Uhrzeit
        for product, time_data in sales_by_product_and_time.items():
            sorted_times = sorted(time_data.keys(), key=lambda d: datetime.strptime(d, "%H:%M:%S"))
            time_values = [time_data[t] for t in sorted_times]
            color = product_colors.get(product, "#6c5ce7")
            ax2.plot(sorted_times, time_values, marker="o", label=product, color=color, linewidth=2)

        ax2.set_title("Verkäufe pro Produkt nach Uhrzeit")
        ax2.set_ylabel("Verkaufte Menge")
        ax2.set_xlabel("Uhrzeit")
        ax2.tick_params(axis="x", rotation=45)
        ax2.legend(loc="upper left", bbox_to_anchor=(1, 1))
        ax2.grid(True, alpha=0.3)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("ascii")

    return render_template(
        "admin_movement_statistics.html",
        img_data=img_data,
        sales_by_product=sales_by_product,
    )


@admin_bp.route("/statistics/inventory-chart")
@_login_required
def inventory_chart():
    """Diagramm für Lagerkennzahlen"""
    products = list(_service.get_all_products().values())
    total_products = len(products)
    total_units = sum(p.quantity for p in products)
    total_value = _service.get_total_inventory_value()

    if not products:
        img_data = None
    else:
        plt.switch_backend("Agg")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)

        # Pie chart für Produktkategorien
        categories = {}
        for p in products:
            category = p.category or "Unkategorisiert"
            categories[category] = categories.get(category, 0) + 1

        if categories:
            ax1.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
            ax1.set_title("Produkte nach Kategorie")
        else:
            ax1.text(0.5, 0.5, 'Keine Kategorien', horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes)

        # Bar chart für Top Produkte nach Wert
        top_by_value = sorted(products, key=lambda p: p.get_total_value(), reverse=True)[:10]
        if top_by_value:
            names = [p.name[:15] + "..." if len(p.name) > 15 else p.name for p in top_by_value]
            values = [p.get_total_value() for p in top_by_value]
            ax2.bar(names, values, color="#6c5ce7")
            ax2.set_title("Top Produkte nach Lagerwert")
            ax2.set_ylabel("Wert (€)")
            ax2.tick_params(axis="x", rotation=45)
        else:
            ax2.text(0.5, 0.5, 'Keine Produkte', horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("ascii")

    return render_template(
        "admin_chart.html",
        img_data=img_data,
        title="Lagerkennzahlen Diagramm",
        back_url=url_for('admin.statistics')
    )


@admin_bp.route("/statistics/movement-chart")
@_login_required
def movement_chart():
    """Diagramm für Bewegungsstatistiken"""
    movements = _service.get_movements()

    if not movements:
        img_data = None
    else:
        plt.switch_backend("Agg")
        fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

        # Bewegungen über Zeit
        movements_by_date = {}
        for m in movements:
            date_key = m.timestamp.strftime("%Y-%m-%d")
            if date_key not in movements_by_date:
                movements_by_date[date_key] = {"IN": 0, "OUT": 0}
            if m.movement_type == "IN":
                movements_by_date[date_key]["IN"] += abs(m.quantity_change)
            else:
                movements_by_date[date_key]["OUT"] += abs(m.quantity_change)

        sorted_dates = sorted(movements_by_date.keys())
        in_values = [movements_by_date[d]["IN"] for d in sorted_dates]
        out_values = [movements_by_date[d]["OUT"] for d in sorted_dates]

        ax.plot(sorted_dates, in_values, marker="o", label="Einlagerungen", color="#00b894", linewidth=2)
        ax.plot(sorted_dates, out_values, marker="s", label="Auslagerungen", color="#e17055", linewidth=2)
        ax.set_title("Bewegungen über Zeit")
        ax.set_ylabel("Menge")
        ax.set_xlabel("Datum")
        ax.tick_params(axis="x", rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("ascii")

    return render_template(
        "admin_chart.html",
        img_data=img_data,
        title="Bewegungsstatistiken Diagramm",
        back_url=url_for('admin.statistics')
    )


@admin_bp.route("/statistics/top-products-chart")
@_login_required
def top_products_chart():
    """Diagramm für Top Produkte"""
    products = list(_service.get_all_products().values())

    if not products:
        img_data = None
    else:
        plt.switch_backend("Agg")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)

        # Top nach Wert
        top_by_value = sorted(products, key=lambda p: p.get_total_value(), reverse=True)[:10]
        if top_by_value:
            names = [p.name[:15] + "..." if len(p.name) > 15 else p.name for p in top_by_value]
            values = [p.get_total_value() for p in top_by_value]
            ax1.barh(names, values, color="#6c5ce7")
            ax1.set_title("Top Produkte nach Lagerwert")
            ax1.set_xlabel("Wert (€)")

        # Top nach Menge
        top_by_quantity = sorted(products, key=lambda p: p.quantity, reverse=True)[:10]
        if top_by_quantity:
            names = [p.name[:15] + "..." if len(p.name) > 15 else p.name for p in top_by_quantity]
            quantities = [p.quantity for p in top_by_quantity]
            ax2.barh(names, quantities, color="#fdcb6e")
            ax2.set_title("Top Produkte nach Menge")
            ax2.set_xlabel("Menge")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("ascii")

    return render_template(
        "admin_chart.html",
        img_data=img_data,
        title="Top Produkte Diagramm",
        back_url=url_for('admin.statistics')
    )


@admin_bp.route("/statistics/categories-chart")
@_login_required
def categories_chart():
    """Diagramm für Produktkategorien"""
    products = list(_service.get_all_products().values())

    categories = {}
    for p in products:
        category = p.category or "Unkategorisiert"
        categories[category] = categories.get(category, 0) + 1

    if not categories:
        img_data = None
    else:
        plt.switch_backend("Agg")
        fig, ax = plt.subplots(figsize=(10, 8), constrained_layout=True)

        ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
        ax.set_title("Produktverteilung nach Kategorien")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("ascii")

    return render_template(
        "admin_chart.html",
        img_data=img_data,
        title="Produktkategorien Diagramm",
        back_url=url_for('admin.statistics')
    )


@admin_bp.route("/statistics/low-stock-chart")
@_login_required
def low_stock_chart():
    """Diagramm für niedrigen Bestand"""
    products = list(_service.get_all_products().values())
    low_stock = [p for p in products if p.quantity <= 10]

    if not low_stock:
        img_data = None
    else:
        plt.switch_backend("Agg")
        fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)

        names = [p.name[:20] + "..." if len(p.name) > 20 else p.name for p in low_stock]
        quantities = [p.quantity for p in low_stock]

        bars = ax.bar(names, quantities, color="#e17055")
        ax.set_title("Produkte mit niedrigem Bestand (≤10)")
        ax.set_ylabel("Bestand")
        ax.set_xlabel("Produkt")
        ax.tick_params(axis="x", rotation=45)

        # Werte über den Balken anzeigen
        for bar, qty in zip(bars, quantities):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   str(qty), ha='center', va='bottom')

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("ascii")

    return render_template(
        "admin_chart.html",
        img_data=img_data,
        title="Niedriger Bestand Diagramm",
        back_url=url_for('admin.statistics')
    )


@admin_bp.route("/statistics/pdf-report")
@_login_required
def pdf_report():
    """PDF-Report mit allen wichtigen Statistiken"""
    # Daten sammeln
    products = list(_service.get_all_products().values())
    movements = _service.get_movements()

    # PDF Buffer erstellen
    buf = io.BytesIO()

    with PdfPages(buf) as pdf:
        # Seite 1: Titel und Zusammenfassung
        fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 Größe
        ax.axis('off')
        ax.text(0.5, 0.9, 'Lager- und Bewegungsstatistiken', ha='center', va='center',
               fontsize=20, fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, 0.8, f'Berichtsdatum: {datetime.now().strftime("%d.%m.%Y %H:%M")}', ha='center', va='center',
               fontsize=12, transform=ax.transAxes)

        # Zusammenfassung
        total_products = len(products)
        total_units = sum(p.quantity for p in products)
        total_value = _service.get_total_inventory_value()
        total_movements = len(movements)

        summary_text = f"""
        Gesamtprodukte: {total_products}
        Gesamteinheiten: {total_units}
        Gesamtwert: {total_value:.2f} €
        Gesamtbewegungen: {total_movements}
        """
        ax.text(0.1, 0.6, summary_text, fontsize=14, verticalalignment='top', fontfamily='monospace')
        pdf.savefig(fig)
        plt.close(fig)

        # Seite 2: Lagerkennzahlen
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.69, 8.27))

        # Pie chart für Kategorien
        categories = {}
        for p in products:
            category = p.category or "Unkategorisiert"
            categories[category] = categories.get(category, 0) + 1

        if categories:
            ax1.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
            ax1.set_title("Produktverteilung nach Kategorien")

        # Top Produkte nach Wert
        top_by_value = sorted(products, key=lambda p: p.get_total_value(), reverse=True)[:10]
        if top_by_value:
            names = [p.name[:15] + "..." if len(p.name) > 15 else p.name for p in top_by_value]
            values = [p.get_total_value() for p in top_by_value]
            ax2.barh(names, values, color="#6c5ce7")
            ax2.set_title("Top 10 Produkte nach Lagerwert")
            ax2.set_xlabel("Wert (€)")

        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # Seite 3: Bewegungsstatistiken
        fig, ax = plt.subplots(figsize=(11.69, 8.27))

        if movements:
            # Bewegungen über Zeit
            movements_by_date = {}
            for m in movements:
                date_key = m.timestamp.strftime("%Y-%m-%d")
                if date_key not in movements_by_date:
                    movements_by_date[date_key] = {"IN": 0, "OUT": 0}
                if m.movement_type == "IN":
                    movements_by_date[date_key]["IN"] += abs(m.quantity_change)
                else:
                    movements_by_date[date_key]["OUT"] += abs(m.quantity_change)

            sorted_dates = sorted(movements_by_date.keys())[-30:]  # Letzte 30 Tage
            in_values = [movements_by_date[d]["IN"] for d in sorted_dates]
            out_values = [movements_by_date[d]["OUT"] for d in sorted_dates]

            ax.plot(sorted_dates, in_values, marker="o", label="Einlagerungen", color="#00b894", linewidth=2)
            ax.plot(sorted_dates, out_values, marker="s", label="Auslagerungen", color="#e17055", linewidth=2)
            ax.set_title("Bewegungen der letzten 30 Tage")
            ax.set_ylabel("Menge")
            ax.set_xlabel("Datum")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Keine Bewegungsdaten verfügbar', ha='center', va='center', transform=ax.transAxes)

        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # Seite 4: Top Produkte und Verkäufe
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11.69, 8.27))

        # Top nach Menge
        top_by_quantity = sorted(products, key=lambda p: p.quantity, reverse=True)[:10]
        if top_by_quantity:
            names = [p.name[:12] + "..." if len(p.name) > 12 else p.name for p in top_by_quantity]
            quantities = [p.quantity for p in top_by_quantity]
            ax1.barh(names, quantities, color="#fdcb6e")
            ax1.set_title("Top Produkte nach Menge")

        # Top bewegte Produkte
        movement_counts = {}
        for m in movements:
            movement_counts[m.product_name] = movement_counts.get(m.product_name, 0) + 1

        top_moved = sorted(movement_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_moved:
            names = [name[:12] + "..." if len(name) > 12 else name for name, _ in top_moved]
            counts = [count for _, count in top_moved]
            ax2.barh(names, counts, color="#74b9ff")
            ax2.set_title("Am meisten bewegte Produkte")

        # Top Verkäufe
        sales_by_product = {}
        for m in movements:
            if m.movement_type == "OUT":
                sales_by_product[m.product_name] = sales_by_product.get(m.product_name, 0) + abs(m.quantity_change)

        top_sold = sorted(sales_by_product.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_sold:
            names = [name[:12] + "..." if len(name) > 12 else name for name, _ in top_sold]
            sold = [amount for _, amount in top_sold]
            ax3.barh(names, sold, color="#e17055")
            ax3.set_title("Top verkaufte Produkte")

        # Niedriger Bestand
        low_stock = [p for p in products if p.quantity <= 10]
        if low_stock:
            names = [p.name[:12] + "..." if len(p.name) > 12 else p.name for p in low_stock[:10]]
            quantities = [p.quantity for p in low_stock[:10]]
            ax4.bar(names, quantities, color="#d63031")
            ax4.set_title("Niedriger Bestand (≤10)")
            ax4.tick_params(axis="x", rotation=45)
        else:
            ax4.text(0.5, 0.5, 'Alle Produkte haben\nausreichend Bestand', ha='center', va='center', transform=ax4.transAxes)

        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f'lager_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )
