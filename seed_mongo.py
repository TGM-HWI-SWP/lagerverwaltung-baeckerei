#!/usr/bin/env python3
"""Seed-Skript zum Vorbefüllen von MongoDB mit Dummy-Daten."""

import json
import os
from datetime import datetime

from src.adapters.mongo_repository import MongoRepository
from src.domain.product import Product


def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value


def load_dummy_data(repo: MongoRepository, json_path: str = "tests/dummy_data.json") -> None:
    if repo.products.count_documents({}) > 0:
        print("MongoDB enthält bereits Produkte. Seed wird übersprungen.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for item in data:
        product = Product(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            price=float(item["price"]),
            quantity=int(item.get("quantity", 0)),
            sku=item.get("sku", ""),
            category=item.get("category", ""),
            created_at=parse_datetime(item.get("created_at")),
            updated_at=parse_datetime(item.get("updated_at")),
            notes=item.get("notes"),
            image=item.get("image"),
        )
        repo.save_product(product)
        count += 1

    print(f"Seed abgeschlossen: {count} Produkte in MongoDB gespeichert.")


if __name__ == "__main__":
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    mongo_db = os.getenv("MONGO_DB", "lagerverwaltung")
    repo = MongoRepository(uri=mongo_uri, db_name=mongo_db)

    try:
        load_dummy_data(repo)
    except Exception as e:
        print(f"Fehler beim Seed-Vorgang: {e}")
        raise
#!/usr/bin/env python3
"""Seed-Skript zum Befüllen von MongoDB mit Dummy-Daten."""

import json
import os
from datetime import datetime

from src.adapters.mongo_repository import MongoRepository
from src.domain.product import Product


def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value


def load_dummy_data(repo: MongoRepository, json_path: str = "tests/dummy_data.json") -> None:
    if repo.products.count_documents({}) > 0:
        print("MongoDB enthält bereits Produkte. Seed wird übersprungen.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for item in data:
        product = Product(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            price=float(item["price"]),
            quantity=int(item.get("quantity", 0)),
            sku=item.get("sku", ""),
            category=item.get("category", ""),
            created_at=parse_datetime(item.get("created_at")),
            updated_at=parse_datetime(item.get("updated_at")),
            notes=item.get("notes"),
            image=item.get("image"),
        )
        repo.save_product(product)
        count += 1

    print(f"Seed abgeschlossen: {count} Produkte in MongoDB gespeichert.")


if __name__ == "__main__":
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    mongo_db = os.getenv("MONGO_DB", "lagerverwaltung")
    repo = MongoRepository(uri=mongo_uri, db_name=mongo_db)

    try:
        load_dummy_data(repo)
    except Exception as e:
        print(f"Fehler beim Seed-Vorgang: {e}")
        raise
