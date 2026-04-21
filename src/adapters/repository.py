"""Repository Adapter - In-Memory und persistente Implementierungen"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..ports import RepositoryPort

try:
    from .mongo_repository import MongoRepository
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False


class InMemoryRepository(RepositoryPort):
    """In-Memory Repository - schnell für Tests und schnelle Prototypen"""

    def __init__(self, load_dummy_data: bool = False):
        self.products: Dict[str, Product] = {}
        self.movements: List[Movement] = []
        if load_dummy_data:
            self._load_dummy_data()

    def _load_dummy_data(self):
        """Dummy-Daten aus JSON-Datei laden für Error Handling"""
        try:
            with open("tests/dummy_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                product = Product(
                    id=item["id"],
                    name=item["name"],
                    description=item["description"],
                    price=item["price"],
                    quantity=item["quantity"],
                    sku=item.get("sku", ""),
                    category=item.get("category", ""),
                    notes=item.get("notes"),
                    image=item.get("image"),
                )
                self.products[product.id] = product
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Warnung: Konnte Dummy-Daten nicht laden: {e}")

    def save_product(self, product: Product) -> None:
        """Produkt im Memory speichern"""
        self.products[product.id] = product

    def load_product(self, product_id: str) -> Optional[Product]:
        """Produkt aus Memory laden"""
        return self.products.get(product_id)

    def load_all_products(self) -> Dict[str, Product]:
        """Alle Produkte aus Memory laden"""
        return self.products.copy()

    def delete_product(self, product_id: str) -> None:
        """Produkt aus Memory löschen"""
        if product_id in self.products:
            del self.products[product_id]

    def save_movement(self, movement: Movement) -> None:
        """Bewegung im Memory speichern"""
        self.movements.append(movement)

    def load_movements(self) -> List[Movement]:
        """Alle Bewegungen aus Memory laden"""
        return self.movements.copy()


class RepositoryFactory:
    """Factory für Repository-Instanzen"""

    @staticmethod
    def create_repository(repository_type: str = "memory") -> RepositoryPort:
        """
        Repository basierend auf Typ erstellen

        Args:
            repository_type: "memory", "mongodb" oder andere (z.B. "sqlite", "json")

        Returns:
            RepositoryPort Instanz
        """
        if repository_type == "memory":
            return InMemoryRepository()
        elif repository_type == "mongodb":
            if not MONGO_AVAILABLE:
                raise ValueError("MongoDB nicht verfügbar. Installiere pymongo: pip install pymongo")
            mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
            mongo_db = os.getenv("MONGO_DB", "lagerverwaltung")
            try:
                mongo_repo = MongoRepository(uri=mongo_uri, db_name=mongo_db)
                # Verbindung testen
                mongo_repo.client.admin.command('ping')
                print(f"✓ MongoDB verbunden: {mongo_uri}")
                return mongo_repo
            except Exception as e:
                print(f"✗ MongoDB-Verbindung fehlgeschlagen: {e}")
                print("→ Fallback auf InMemory Repository mit dummy_data.json")
                return InMemoryRepository(load_dummy_data=True)
        else:
            raise ValueError(f"Unbekannter Repository-Typ: {repository_type}")
