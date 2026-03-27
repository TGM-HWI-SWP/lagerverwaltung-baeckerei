"""Movement Report - Bewegungsprotokoll für Produkte"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional


class MovementType(Enum):
    """Typen von Lagerbewegungen"""
    EINGANG = "Eingang"
    AUSGANG = "Ausgang"
    BESTANDSKORREKTUR = "Bestandskorrektur"
    BESTANDSPRÜFUNG = "Bestandsprüfung"
    RÜCKGABE = "Rückgabe"
    BESCHÄDIGT = "Beschädigt"
    VERLOREN = "Verloren"


@dataclass
class Movement:
    """Einzelne Lagerbewegung"""

    product_id: str
    product_name: str
    movement_type: MovementType
    quantity_change: int
    timestamp: datetime = field(default_factory=datetime.now)
    reason: Optional[str] = None
    performed_by: str = "System"

    def __post_init__(self):
        """Validierung nach Initialisierung"""
        if not self.product_id:
            raise ValueError("Produkt-ID kann nicht leer sein")
        if self.quantity_change == 0:
            raise ValueError("Mengenmenge kann nicht 0 sein")


class MovementReport:
    """Bewegungsprotokoll für Produkte - verwaltet und analysiert Lagerbewegungen"""

    def __init__(self):
        """Initialisiere das Bewegungsprotokoll"""
        self.movements: List[Movement] = []

    def add_movement(self, movement: Movement) -> None:
        """
        Bewegung hinzufügen

        Args:
            movement: Die hinzuzufügende Bewegung
        """
        if not isinstance(movement, Movement):
            raise TypeError("Argument muss eine Movement-Instanz sein")
        self.movements.append(movement)

    def add_movements(self, movements: List[Movement]) -> None:
        """
        Mehrere Bewegungen hinzufügen

        Args:
            movements: Liste von Bewegungen
        """
        for movement in movements:
            self.add_movement(movement)

    def get_movements_by_product(self, product_id: str) -> List[Movement]:
        """
        Alle Bewegungen für ein bestimmtes Produkt abrufen

        Args:
            product_id: ID des Produkts

        Returns:
            Liste der Bewegungen für dieses Produkt
        """
        return [m for m in self.movements if m.product_id == product_id]

    def get_movements_by_type(self, movement_type: MovementType) -> List[Movement]:
        """
        Alle Bewegungen eines bestimmten Typs abrufen

        Args:
            movement_type: Typ der Bewegung

        Returns:
            Liste der Bewegungen dieses Typs
        """
        return [m for m in self.movements if m.movement_type == movement_type]

    def get_movements_by_date_range(self, start: datetime, end: datetime) -> List[Movement]:
        """
        Bewegungen in einem Zeitbereich abrufen

        Args:
            start: Startdatum
            end: Enddatum

        Returns:
            Liste der Bewegungen im Zeitbereich
        """
        return [m for m in self.movements if start <= m.timestamp <= end]

    def get_total_quantity_change(self, product_id: str) -> int:
        """
        Gesamtmengenänderung für ein Produkt berechnen

        Args:
            product_id: ID des Produkts

        Returns:
            Gesamte Mengenänderung
        """
        movements = self.get_movements_by_product(product_id)
        return sum(m.quantity_change for m in movements)

    def get_movement_statistics(self) -> Dict:
        """
        Statistiken über alle Bewegungen abrufen

        Returns:
            Dictionary mit Statistiken
        """
        if not self.movements:
            return {
                "total_movements": 0,
                "total_products_affected": 0,
                "movement_types": {},
                "total_quantity_change": 0
            }

        movement_types = {}
        for movement_type in MovementType:
            count = len(self.get_movements_by_type(movement_type))
            if count > 0:
                movement_types[movement_type.value] = count

        affected_products = set(m.product_id for m in self.movements)

        total_quantity = sum(m.quantity_change for m in self.movements)

        return {
            "total_movements": len(self.movements),
            "total_products_affected": len(affected_products),
            "movement_types": movement_types,
            "total_quantity_change": total_quantity,
            "first_movement": min(self.movements, key=lambda m: m.timestamp).timestamp,
            "last_movement": max(self.movements, key=lambda m: m.timestamp).timestamp
        }

    def get_sorted_movements(self, reverse: bool = False) -> List[Movement]:
        """
        Bewegungen sortiert nach Zeitstempel abrufen

        Args:
            reverse: Wenn True, in absteigender Reihenfolge

        Returns:
            Sortierte Liste der Bewegungen
        """
        return sorted(self.movements, key=lambda m: m.timestamp, reverse=reverse)

    def clear(self) -> None:
        """Alle Bewegungen löschen"""
        self.movements.clear()
