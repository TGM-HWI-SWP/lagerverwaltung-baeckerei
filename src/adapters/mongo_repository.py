"""MongoDB Adapter als alternatives Repository"""

import os
from typing import Dict, List, Optional

from pymongo import MongoClient

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..ports import RepositoryPort


def _dict_to_product(data: dict) -> Product:
    return Product(
        id=data["id"],
        name=data.get("name", ""),
        description=data.get("description", ""),
        price=float(data.get("price", 0.0)),
        quantity=int(data.get("quantity", 0)),
        category=data.get("category", ""),
    )


def _movement_from_doc(doc: dict) -> Movement:
    return Movement(
        id=doc["id"],
        product_id=doc["product_id"],
        product_name=doc.get("product_name", ""),
        quantity_change=int(doc.get("quantity_change", 0)),
        movement_type=doc.get("movement_type", ""),
        reason=doc.get("reason", ""),
        performed_by=doc.get("performed_by", ""),
        timestamp=doc.get("timestamp"),
    )


class MongoRepository(RepositoryPort):
    """MongoDB-basierte Repository-Implementierung"""

    def __init__(self, uri: Optional[str] = None, db_name: str = "lagerverwaltung"):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://mongo:27017/")
        self.db_name = db_name
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.products = self.db["products"]
        self.movements = self.db["movements"]

    def save_product(self, product: Product) -> None:
        self.products.replace_one({"id": product.id}, product.__dict__, upsert=True)

    def load_product(self, product_id: str) -> Optional[Product]:
        doc = self.products.find_one({"id": product_id})
        return _dict_to_product(doc) if doc else None

    def load_all_products(self) -> Dict[str, Product]:
        result: Dict[str, Product] = {}
        for doc in self.products.find():
            product = _dict_to_product(doc)
            result[product.id] = product
        return result

    def delete_product(self, product_id: str) -> None:
        self.products.delete_one({"id": product_id})

    def save_movement(self, movement: Movement) -> None:
        self.movements.insert_one(movement.__dict__)

    def load_movements(self) -> List[Movement]:
        return [_movement_from_doc(doc) for doc in self.movements.find()]
