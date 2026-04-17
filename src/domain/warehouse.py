"""Warehouse Domain Model"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from .product import Product


@dataclass
class Movement:
    """Bewegungsprotokoll-Eintrag für Lagerbestände"""

    id: str
    product_id: str
    product_name: str
    quantity_change: int
    movement_type: str  # z.B. "IN", "OUT", "CORRECTION"
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    performed_by: str = "system"


class Warehouse:
    """Verwaltungsklasse für das Lager"""

    def __init__(self, name: str):
        self.name = name
        self.products: Dict[str, Product] = {}
        self.movements: list[Movement] = []

    def add_product(self, product: Product) -> None:
        """Produkt zum Lager hinzufügen"""
        if product.id in self.products:
            raise ValueError(f"Produkt mit ID {product.id} existiert bereits")
        self.products[product.id] = product

    def get_product(self, product_id: str) -> Optional[Product]:
        """Produkt nach ID abrufen"""
        return self.products.get(product_id)

    def record_movement(self, movement: Movement) -> None:
        """Lagerbewegung protokollieren"""
        if movement.product_id not in self.products:
            raise ValueError(
                f"Produkt mit ID {movement.product_id} existiert nicht"
            )
        self.movements.append(movement)

    def get_total_inventory_value(self) -> float:
        """Gesamtwert aller Bestände berechnen"""
        return sum(product.get_total_value() for product in self.products.values())

    def get_inventory_report(self) -> Dict[str, dict]:
        """
        Lagerbestandsbericht erstellen

        Returns:
            Dictionary mit Produktinformationen
        """
        return {
            product_id: {
                "name": product.name,
                "quantity": product.quantity,
                "price": product.price,
                "total_value": product.get_total_value(),
            }
            for product_id, product in self.products.items()
        }

    def get_movement_report(self) -> Dict[str, dict]:
        """
        Bewegungsbericht für alle Produkte erstellen

        Returns:
            Dictionary mit Bewegungsstatistiken pro Produkt
        """
        report = {}
        for product_id, product in self.products.items():
            movements = [m for m in self.movements if m.product_id == product_id]
            if movements:
                total_change = sum(m.quantity_change for m in movements)
                in_movements = [m for m in movements if m.movement_type == "IN"]
                out_movements = [m for m in movements if m.movement_type == "OUT"]
                corrections = [m for m in movements if m.movement_type == "CORRECTION"]

                report[product_id] = {
                    "name": product.name,
                    "total_movements": len(movements),
                    "total_quantity_change": total_change,
                    "in_movements": len(in_movements),
                    "out_movements": len(out_movements),
                    "corrections": len(corrections),
                    "first_movement": min(movements, key=lambda m: m.timestamp).timestamp if movements else None,
                    "last_movement": max(movements, key=lambda m: m.timestamp).timestamp if movements else None,
                }
        return report

    def get_movements_by_product(self, product_id: str) -> list[Movement]:
        """
        Alle Bewegungen für ein bestimmtes Produkt abrufen

        Args:
            product_id: ID des Produkts

        Returns:
            Liste der Bewegungen
        """
        return [m for m in self.movements if m.product_id == product_id]

    def get_movements_by_type(self, movement_type: str) -> list[Movement]:
        """
        Alle Bewegungen eines bestimmten Typs abrufen

        Args:
            movement_type: Typ der Bewegung ("IN", "OUT", "CORRECTION")

        Returns:
            Liste der Bewegungen
        """
        return [m for m in self.movements if m.movement_type == movement_type]

    def get_movement_statistics(self) -> Dict[str, int]:
        """
        Gesamtstatistiken über alle Bewegungen

        Returns:
            Dictionary mit Statistiken
        """
        if not self.movements:
            return {"total_movements": 0, "total_quantity_change": 0}

        total_change = sum(m.quantity_change for m in self.movements)
        return {
            "total_movements": len(self.movements),
            "total_quantity_change": total_change,
            "in_movements": len([m for m in self.movements if m.movement_type == "IN"]),
            "out_movements": len([m for m in self.movements if m.movement_type == "OUT"]),
            "corrections": len([m for m in self.movements if m.movement_type == "CORRECTION"]),
        }
