"""Demo-Script für MovementReport - Schneller Test ohne pytest"""

import sys
from pathlib import Path

# Pfad zur src-Verzeichnis hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from src.reports.movement import Movement, MovementType, MovementReport


def demo_movement_report():
    """Demonstriert die MovementReport-Klasse mit praktischen Beispielen"""

    print("=" * 80)
    print("DEMO: MovementReport für Lagerverwaltung")
    print("=" * 80)
    print()

    # Schritt 1: Report erstellen
    report = MovementReport()
    print("✓ MovementReport erstellt")
    print()

    # Schritt 2: Bewegungen hinzufügen
    print("-" * 80)
    print("Lagerbewegungen hinzufügen...")
    print("-" * 80)

    movements = [
        Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.EINGANG,
            quantity_change=100,
            reason="Lieferung Bäckerei Meyer",
            performed_by="Max Müller"
        ),
        Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.AUSGANG,
            quantity_change=-25,
            reason="Verkauf",
            performed_by="Anna Schmidt"
        ),
        Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.AUSGANG,
            quantity_change=-15,
            reason="Verkauf",
            performed_by="Anna Schmidt"
        ),
        Movement(
            product_id="CROISSANT001",
            product_name="Croissant",
            movement_type=MovementType.EINGANG,
            quantity_change=50,
            reason="Lieferung",
            performed_by="System"
        ),
        Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.BESCHÄDIGT,
            quantity_change=-3,
            reason="Während Transport beschädigt",
            performed_by="QC"
        ),
        Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.BESTANDSPRÜFUNG,
            quantity_change=2,
            reason="Inventur Korrektur",
            performed_by="Inventory Team"
        ),
    ]

    report.add_movements(movements)
    print(f"✓ {len(movements)} Bewegungen hinzugefügt")
    print()

    # Schritt 3: Statistiken anzeigen
    print("-" * 80)
    print("STATISTIKEN")
    print("-" * 80)
    stats = report.get_movement_statistics()
    print(f"Gesamt Bewegungen: {stats['total_movements']}")
    print(f"Betroffene Produkte: {stats['total_products_affected']}")
    print(f"Gesamte Mengenänderung: {stats['total_quantity_change']}")
    print(f"Bewegungstypen: {stats['movement_types']}")
    print(f"Zeitspanne: {stats['first_movement']} bis {stats['last_movement']}")
    print()

    # Schritt 4: Bewegungen nach Produkt
    print("-" * 80)
    print("BEWEGUNGEN FÜR BREAD001")
    print("-" * 80)
    bread_movements = report.get_movements_by_product("BREAD001")
    print(f"Anzahl: {len(bread_movements)}")
    total_change = report.get_total_quantity_change("BREAD001")
    print(f"Gesamte Mengenänderung: {total_change:+d}")
    print()

    # Schritt 5: Bewegungen nach Typ
    print("-" * 80)
    print("BEWEGUNGEN NACH TYP")
    print("-" * 80)
    for move_type in MovementType:
        movements_of_type = report.get_movements_by_type(move_type)
        if movements_of_type:
            print(f"{move_type.value}: {len(movements_of_type)} Stück")
    print()

    # Schritt 6: Chronologische Übersicht
    print("-" * 80)
    print("CHRONOLOGISCHE ÜBERSICHT (älteste zuerst)")
    print("-" * 80)
    sorted_movements = report.get_sorted_movements(reverse=False)
    for i, movement in enumerate(sorted_movements, 1):
        time_str = movement.timestamp.strftime("%H:%M:%S")
        print(
            f"{i}. [{time_str}] {movement.product_name} | "
            f"{movement.movement_type.value:20} | "
            f"{movement.quantity_change:+4} | "
            f"von {movement.performed_by}"
        )
        if movement.reason:
            print(f"   Grund: {movement.reason}")
    print()

    # Schritt 7: Fehlerbehandlung testen
    print("-" * 80)
    print("FEHLERBEHANDLUNG TESTEN")
    print("-" * 80)

    try:
        invalid_movement = Movement(
            product_id="",
            product_name="Test",
            movement_type=MovementType.EINGANG,
            quantity_change=10
        )
    except ValueError as e:
        print(f"✓ Fehler erkannt (leere ID): {e}")

    try:
        invalid_movement = Movement(
            product_id="P001",
            product_name="Test",
            movement_type=MovementType.EINGANG,
            quantity_change=0
        )
    except ValueError as e:
        print(f"✓ Fehler erkannt (Menge 0): {e}")

    try:
        report.add_movement("Keine gültige Bewegung")
    except TypeError as e:
        print(f"✓ Fehler erkannt (Typ-Fehler): {e}")

    print()
    print("=" * 80)
    print("✓ DEMO ERFOLGREICH ABGESCHLOSSEN")
    print("=" * 80)


if __name__ == "__main__":
    demo_movement_report()
