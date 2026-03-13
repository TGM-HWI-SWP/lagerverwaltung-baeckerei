# Schnittstellen-Dokumentation (Contracts)

## Übersicht

Diese Datei dokumentiert alle externen Schnittstellen des Projekts. Sie wird von Rolle 1 (Contract Owner) gepflegt und aktualisiert bei jeder Änderung.

---

## 1. RepositoryPort

**Verantwortlich:** Rolle 2 (Businesslogik)

### Beschreibung
Abstrakte Schnittstelle für Datenpersistenz. Ermöglicht den Austausch zwischen verschiedenen Speicheradaptern (In-Memory, SQLite, JSON, etc.)

### Methoden

#### `save_product(product: Product) -> None`
Speichert ein Produkt.

**Parameter:**
- `product`: Product-Instanz

**Exceptions:**
- Keine

**Implementierungen:**
- `InMemoryRepository` (v0.2)

#### `load_product(product_id: str) -> Optional[Product]`
Lädt ein einzelnes Produkt.

**Parameter:**
- `product_id`: Eindeutige Produkt-ID

**Return:**
- `Product` oder `None` falls nicht gefunden

**Implementierungen:**
- `InMemoryRepository` (v0.2)

#### `load_all_products() -> Dict[str, Product]`
Lädt alle Produkte.

**Return:**
- Dictionary mit Product-IDs als Keys

**Implementierungen:**
- `InMemoryRepository` (v0.2)

#### `delete_product(product_id: str) -> None`
Löscht ein Produkt.

**Parameter:**
- `product_id`: Eindeutige Produkt-ID

**Exceptions:**
- Keine (ignoriert unbekannte IDs)

**Implementierungen:**
- `InMemoryRepository` (v0.2)

#### `save_movement(movement: Movement) -> None`
Speichert eine Lagerbewegung.

**Parameter:**
- `movement`: Movement-Instanz

**Implementierungen:**
- `InMemoryRepository` (v0.2)

#### `load_movements() -> List[Movement]`
Lädt alle Lagerbewegungen.

**Return:**
- Liste von Movement-Objekten

**Implementierungen:**
- `InMemoryRepository` (v0.2)

---

## 2. ReportPort

**Verantwortlich:** Rolle 3 (Reports & Qualität)

### Beschreibung
Abstrakte Schnittstelle für Report-Generierung.

### Methoden

#### `generate_inventory_report() -> str`
Generiert einen Lagerbestandsbericht.

**Return:**
- Formatierter String-Bericht

**Implementierungen:**
- `ConsoleReportAdapter` (v0.2)

#### `generate_movement_report() -> str`
Generiert ein Bewegungsprotokoll.

**Return:**
- Formatierter String-Bericht

**Implementierungen:**
- `ConsoleReportAdapter` (v0.2)

---

## 3. WarehouseService

**Verantwortlich:** Rolle 2 (Businesslogik)

### Beschreibung
Service-Klasse für zentrale Lagerverwaltungslogik.

### Methoden

#### `create_product(...) -> Product`
Erstellt ein neues Produkt.

**Parameter:**
- `product_id: str` - Eindeutige ID
- `name: str` - Produktname
- `description: str` - Beschreibung
- `price: float` - Preis
- `category: str` - Kategorie (optional)
- `initial_quantity: int` - Anfangsbestand

**Return:**
- Neue Product-Instanz

**Exceptions:**
- `ValueError`: Bei ungültigen Eingaben

#### `add_to_stock(product_id: str, quantity: int, reason: str, user: str) -> None`
Erhöht den Bestand.

**Parameter:**
- `product_id: str`
- `quantity: int` - Menge
- `reason: str` - Grund (optional)
- `user: str` - Benutzer (default: "system")

**Exceptions:**
- `ValueError`: Wenn Produkt nicht existiert

#### `remove_from_stock(product_id: str, quantity: int, reason: str, user: str) -> None`
Verringert den Bestand.

**Parameter:**
- `product_id: str`
- `quantity: int` - Menge
- `reason: str` - Grund (optional)
- `user: str` - Benutzer (default: "system")

**Exceptions:**
- `ValueError`: Wenn Bestand unzureichend oder Produkt nicht existiert

#### `get_product(product_id: str) -> Optional[Product]`
Ruft ein einzelnes Produkt ab.

**Return:**
- Product oder None

#### `get_all_products() -> Dict[str, Product]`
Ruft alle Produkte ab.

**Return:**
- Dictionary mit allen Produkten

#### `get_movements() -> List[Movement]`
Ruft alle Lagerbewegungen ab.

**Return:**
- Liste aller Movements

#### `get_total_inventory_value() -> float`
Berechnet den Gesamtwert des Lagers.

**Return:**
- Wert in Euro

---

## 4. Domain Models

*Hinweis: Der nachfolgende Abschnitt beschreibt den aktuellen Stand der Implementierung (v0.2).* 


### Product

**Hinweis:** Die Klasse ist vollständig implementiert. Änderungen werden in v0.3 dokumentiert.

**Attribute:**
- `id: str` - Eindeutige ID
- `name: str` - Produktname
- `description: str` - Beschreibung
- `price: float` - Preis pro Einheit
- `quantity: int` - Bestand
- `sku: str` - Stock Keeping Unit
- `category: str` - Kategorie
- `created_at: datetime` - Erstellungsdatum
- `updated_at: datetime` - Änderungsdatum
- `notes: str` - Anmerkungen

**Methoden:**

**Exceptions:**
- `ValueError` bei negativer Menge oder Preis
- `update_quantity(amount: int) -> None` - Bestand ändern
- `get_total_value() -> float` - Gesamtwert berechnen

### Movement

**Hinweis:** derzeit werden nur Typen "IN" und "OUT" verwendet. Der Eintrag "CORRECTION" ist geplant, aber noch nicht aktiv.

**Attribute:**
- `id: str` - Eindeutige Bewegungs-ID
- `product_id: str` - Verweis auf Produkt
- `product_name: str` - Name des Produkts
- `quantity_change: int` - Mengenänderung (+/-)
- `movement_type: str` - "IN", "OUT", "CORRECTION"
- `reason: str` - Grund (optional)
- `timestamp: datetime` - Zeitstempel
- `performed_by: str` - Benutzer

---

## 5. UI-Komponenten

**Verantwortlich:** Rolle 4 (GUI)

### WarehouseMainWindow
Fenster mit Tab-Widget.

**Methoden / Schnittstellen:**
- `show_products(products: Dict[str, Product]) -> None` – zeigt Liste der Produkte
- `show_movements(movements: List[Movement]) -> None` – zeigt Bewegungsprotokoll (aktuell leer)
- `show_inventory_report(report: str) -> None` – präsentiert Bestandsbericht
- `show_movement_report(report: str) -> None` – präsentiert Bewegungsbericht
- `get_new_product_data() -> Dict` – liest Benutzereingaben aus Produktdialog
- `get_edit_product_data(product_id: str) -> Dict` – (noch nicht implementiert)
- `delete_product_request(product_id: str) -> None` – wird angestoßen, derzeit Stub (muss von Role 4 implementiert)

**Exceptions:**
- Keine – GUI steuert interne Validierungen.

### ProductDialogWindow
Dialog für Produktdaten.

**Methoden:**
- `open(product: Optional[Product] = None) -> Dict` – öffnet Dialog; gibt Eingaben zurück oder `None` bei Abbruch

**Hinweis:** Lösch- und Bearbeiten-Funktionen sind als TODO markiert.

---

## Versionshistorie der Contracts

### v0.1 (2025-01-20)
- RepositoryPort: Grundlegende CRUD-Operationen
- ReportPort: Basis-Report-Generierung
- WarehouseService: Kern-Use-Cases
- Product: Basis-Domain-Model
- Movement: Lagerbewegungen-Protokoll

### v0.2 (2026-03-13)
- Dokumentation an aktuelles Walking-Skeleton angepasst
- UI-Komponenten hinzugefügt und beschrieben
- Fehlerbehandlungen für Service-Methoden spezifiziert
- Versionsnummern angehoben

---

## Zukünftige Änderungen

- [ ] SQLite-Adapter implementieren
- [ ] GraphML-Report-Generierung
- [ ] Benutzer-Management erweitern
- [ ] Batch-Operationen unterstützen
