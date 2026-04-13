"""Tests für MovementReport und Movement-Klassen"""

# Immer ausführen mit "python -m tests.unit.test_movement_report"

import pytest
from datetime import datetime, timedelta
from src.reports.movement import Movement, MovementType, MovementReport

class TestMovement:
    """Tests für die Movement-Klasse"""

    def test_movement_creation(self):
        """Test: Bewegung erstellen"""
        movement = Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.EINGANG,
            quantity_change=10,
            reason="Neuer Einkauf"
        )
        assert movement.product_id == "P001"
        assert movement.product_name == "Brot"
        assert movement.quantity_change == 10
        assert movement.movement_type == MovementType.EINGANG

    def test_movement_validation_empty_id(self):
        """Test: Bewegung mit leerer ID sollte fehlschlagen"""
        with pytest.raises(ValueError, match="Produkt-ID kann nicht leer sein"):
            Movement(
                product_id="",
                product_name="Brot",
                movement_type=MovementType.EINGANG,
                quantity_change=10
            )

    def test_movement_validation_zero_quantity(self):
        """Test: Bewegung mit Menge 0 sollte fehlschlagen"""
        with pytest.raises(ValueError, match="Mengenmenge kann nicht 0 sein"):
            Movement(
                product_id="P001",
                product_name="Brot",
                movement_type=MovementType.EINGANG,
                quantity_change=0
            )

    def test_movement_default_timestamp(self):
        """Test: Bewegung erhält automatisch einen Zeitstempel"""
        before = datetime.now()
        movement = Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.AUSGANG,
            quantity_change=-5
        )
        after = datetime.now()
        assert before <= movement.timestamp <= after

    def test_movement_default_performed_by(self):
        """Test: Bewegung hat Standard-Benutzer"""
        movement = Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.EINGANG,
            quantity_change=5
        )
        assert movement.performed_by == "System"


class TestMovementReport:
    """Tests für die MovementReport-Klasse"""

    @pytest.fixture
    def report(self):
        """Fixture für leeres MovementReport"""
        return MovementReport()

    @pytest.fixture
    def sample_movements(self):
        """Fixture mit Beispiel-Bewegungen"""
        movements = [
            Movement(
                product_id="P001",
                product_name="Vollkornbrot",
                movement_type=MovementType.EINGANG,
                quantity_change=50,
                reason="Lieferung Bäckerei Meyer"
            ),
            Movement(
                product_id="P001",
                product_name="Vollkornbrot",
                movement_type=MovementType.AUSGANG,
                quantity_change=-10,
                reason="Verkauf",
                performed_by="Anna Schmidt"
            ),
            Movement(
                product_id="P002",
                product_name="Croissant",
                movement_type=MovementType.EINGANG,
                quantity_change=30,
                reason="Lieferung"
            ),
            Movement(
                product_id="P001",
                product_name="Vollkornbrot",
                movement_type=MovementType.BESCHÄDIGT,
                quantity_change=-2,
                reason="Während Transport beschädigt"
            )
        ]
        return movements

    def test_report_initialization(self, report):
        """Test: Report wird leer initialisiert"""
        assert len(report.movements) == 0

    def test_add_single_movement(self, report):
        """Test: Einzelne Bewegung hinzufügen"""
        movement = Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.EINGANG,
            quantity_change=10
        )
        report.add_movement(movement)
        assert len(report.movements) == 1
        assert report.movements[0].product_id == "P001"

    def test_add_multiple_movements(self, report, sample_movements):
        """Test: Mehrere Bewegungen hinzufügen"""
        report.add_movements(sample_movements)
        assert len(report.movements) == 4

    def test_add_invalid_movement(self, report):
        """Test: Ungültige Bewegung sollte fehlschlagen"""
        with pytest.raises(TypeError):
            report.add_movement("Not a Movement")

    def test_get_movements_by_product(self, report, sample_movements):
        """Test: Bewegungen nach Produkt filtern"""
        report.add_movements(sample_movements)
        p001_movements = report.get_movements_by_product("P001")
        assert len(p001_movements) == 3
        assert all(m.product_id == "P001" for m in p001_movements)

    def test_get_movements_by_type(self, report, sample_movements):
        """Test: Bewegungen nach Typ filtern"""
        report.add_movements(sample_movements)
        eingang = report.get_movements_by_type(MovementType.EINGANG)
        assert len(eingang) == 2
        assert all(m.movement_type == MovementType.EINGANG for m in eingang)

    def test_get_movements_by_date_range(self, report):
        """Test: Bewegungen nach Zeitbereich filtern"""
        now = datetime.now()
        earlier = now - timedelta(hours=1)
        later = now + timedelta(hours=1)

        report.add_movement(Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.EINGANG,
            quantity_change=10,
            timestamp=now
        ))

        result = report.get_movements_by_date_range(earlier, later)
        assert len(result) == 1

        result = report.get_movements_by_date_range(later, later + timedelta(hours=1))
        assert len(result) == 0

    def test_get_total_quantity_change(self, report, sample_movements):
        """Test: Gesamtmengenänderung berechnen"""
        report.add_movements(sample_movements)
        # P001: +50 - 10 - 2 = 38
        total = report.get_total_quantity_change("P001")
        assert total == 38
        # P002: +30
        total = report.get_total_quantity_change("P002")
        assert total == 30

    def test_get_movement_statistics_empty(self, report):
        """Test: Statistiken für leeren Report"""
        stats = report.get_movement_statistics()
        assert stats["total_movements"] == 0
        assert stats["total_products_affected"] == 0
        assert stats["movement_types"] == {}

    def test_get_movement_statistics_filled(self, report, sample_movements):
        """Test: Statistiken mit Bewegungen"""
        report.add_movements(sample_movements)
        stats = report.get_movement_statistics()

        assert stats["total_movements"] == 4
        assert stats["total_products_affected"] == 2
        assert stats["movement_types"]["Eingang"] == 2
        assert stats["movement_types"]["Ausgang"] == 1
        assert stats["movement_types"]["Beschädigt"] == 1
        assert stats["total_quantity_change"] == 68  # 50 - 10 + 30 - 2

    def test_get_sorted_movements(self, report):
        """Test: Bewegungen sortieren"""
        now = datetime.now()
        m1 = Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.EINGANG,
            quantity_change=10,
            timestamp=now
        )
        m2 = Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.AUSGANG,
            quantity_change=-5,
            timestamp=now + timedelta(hours=1)
        )
        m3 = Movement(
            product_id="P001",
            product_name="Brot",
            movement_type=MovementType.EINGANG,
            quantity_change=20,
            timestamp=now + timedelta(hours=2)
        )

        report.add_movements([m3, m1, m2])  # Ungeordnet hinzufügen
        sorted_asc = report.get_sorted_movements(reverse=False)
        assert sorted_asc[0].timestamp == now
        assert sorted_asc[2].timestamp == now + timedelta(hours=2)

        sorted_desc = report.get_sorted_movements(reverse=True)
        assert sorted_desc[0].timestamp == now + timedelta(hours=2)
        assert sorted_desc[2].timestamp == now

    def test_clear_movements(self, report, sample_movements):
        """Test: Alle Bewegungen löschen"""
        report.add_movements(sample_movements)
        assert len(report.movements) == 4
        report.clear()
        assert len(report.movements) == 0


class TestMovementIntegration:
    """Integrations-Tests für Bewegungsprotokoll-Workflow"""

    def test_complete_workflow(self):
        """Test: Kompletter Workflow mit mehreren Produkten"""
        report = MovementReport()

        # Lieferung Bäckerei 1
        report.add_movement(Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.EINGANG,
            quantity_change=100,
            reason="Morgens vom Bäcker",
            performed_by="Max Müller"
        ))

        # Verkäufe
        report.add_movement(Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.AUSGANG,
            quantity_change=-15,
            reason="Verkauf",
            performed_by="Sales"
        ))

        # Beschädigte Ware
        report.add_movement(Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.BESCHÄDIGT,
            quantity_change=-3,
            reason="Schimmel entdeckt",
            performed_by="QC"
        ))

        # Bestandsprüfung
        report.add_movement(Movement(
            product_id="BREAD001",
            product_name="Vollkornbrot",
            movement_type=MovementType.BESTANDSPRÜFUNG,
            quantity_change=2,
            reason="Inventur Korrektur",
            performed_by="Inventory"
        ))

        # Überprüfungen
        stats = report.get_movement_statistics()
        assert stats["total_movements"] == 4
        assert report.get_total_quantity_change("BREAD001") == 84  # 100 - 15 - 3 + 2
        assert len(report.get_movements_by_type(MovementType.EINGANG)) == 1
