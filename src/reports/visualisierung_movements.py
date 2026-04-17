import matplotlib.pyplot as plt
from typing import Dict
from datetime import datetime
from src.reports.movement import MovementReport, Movement, MovementType
from src.reports.visualisierung_movements import MovementDarstellung

report = MovementReport()

report.add_movement(Movement("1", "Brot", MovementType.EINGANG, 10))
report.add_movement(Movement("1", "Brot", MovementType.AUSGANG, -3))
report.add_movement(Movement("2", "Kuchen", MovementType.EINGANG, 5))

visualizer = MovementDarstellung(report)
visualizer.plot_all()




from src.reports.movement import MovementReport


class MovementDarstellung:
    """Visualisiert MovementReport-Daten mit matplotlib"""

    def __init__(self, report: MovementReport):
        self.report = report

    def plot_movement_types(self) -> None:
        """Balkendiagramm für Bewegungstypen"""
        stats = self.report.get_movement_statistics()

        if not stats["movement_types"]:
            print("Keine Daten für Bewegungstypen")
            return

        plt.figure()
        plt.title("Bewegungstypen (Movement Types)")

        plt.bar(stats["movement_types"].keys(), stats["movement_types"].values())

        plt.xlabel("Bewegungstyp (Movement Type)")
        plt.ylabel("Anzahl (Count)")

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_product_changes(self) -> None:
        """Mengenänderung pro Produkt"""
        movements = self.report.movements

        if not movements:
            print("Keine Daten für Produkte")
            return

        product_changes: Dict[str, int] = {}

        for m in movements:
            product_changes[m.product_name] = (
                product_changes.get(m.product_name, 0) + m.quantity_change
            )

        plt.figure()
        plt.title("Mengenänderung pro Produkt (Quantity Change per Product)")

        plt.bar(product_changes.keys(), product_changes.values())

        plt.xlabel("Produkt (Product)")
        plt.ylabel("Mengenänderung (Quantity Change)")

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_inventory_over_time(self) -> None:
        """Zeitverlauf der Bestandsänderung"""
        movements = self.report.get_sorted_movements()

        if not movements:
            print("Keine Zeitdaten vorhanden")
            return

        times = [m.timestamp for m in movements]

        cumulative = 0
        quantities = []

        for m in movements:
            cumulative += m.quantity_change
            quantities.append(cumulative)

        plt.figure()
        plt.title("Bestandsverlauf (Inventory Over Time)")

        plt.plot(times, quantities)

        plt.xlabel("Zeit (Time)")
        plt.ylabel("Kumulierte Menge (Cumulative Quantity)")

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_all(self) -> None:
        """Alle Diagramme anzeigen"""
        self.plot_movement_types()
        self.plot_product_changes()
        self.plot_inventory_over_time()