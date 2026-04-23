# Schnittstellen-Dokumentation (Contracts)

## Übersicht

Diese Datei dokumentiert alle externen Schnittstellen des Projekts. Sie wird von Rolle 1 (Contract Owner) gepflegt und bei jeder Änderung versioniert.

Die Contracts definieren die Zusammenarbeit zwischen:

* UI ↔ Services
* Services ↔ Repository (Ports)
* Services ↔ Reports

Ziel ist eine klare Trennung von Businesslogik und Infrastruktur gemäß Port-/Adapter-Architektur.

---

## 1. RepositoryPort

**Verantwortlich:** Rolle 2 (Businesslogik)

### Beschreibung

Abstrakte Schnittstelle für Datenpersistenz. Ermöglicht den Austausch zwischen verschiedenen Speicheradaptern.

Aktuelle Implementierungen:

* `InMemoryRepository`
* `MongoRepository`

Auswahl erfolgt über `RepositoryFactory` (`memory` / `mongodb`).

---

### Methoden

#### `save_product(product: Product) -> None`

Speichert ein Produkt.

**Parameter:**

* `product`: Product-Instanz (darf nicht None sein)

**Preconditions:**

* product.id ist eindeutig
* product ist valide (siehe Domain-Regeln)

**Postconditions:**

* Produkt ist persistent gespeichert oder aktualisiert

**Exceptions:**

* ValueError: wenn product None ist oder ungültige Daten enthält

**Verwendet in:**

* Produkt anlegen
* Produkt aktualisieren

---

#### `load_product(product_id: str) -> Optional[Product]`

Lädt ein einzelnes Produkt.

**Parameter:**

* `product_id`: eindeutige Produkt-ID (nicht leer)

**Return:**

* Product → falls gefunden
* None → falls nicht vorhanden

**Preconditions:**

* product_id darf nicht leer sein

**Exceptions:**

* ValueError: wenn product_id leer ist

**Verwendet in:**

* Produkt anzeigen
* Lagerbestand ändern

---

#### `load_all_products() -> Dict[str, Product]`

Lädt alle Produkte.

**Return:**

* Dictionary mit Produkt-ID als Key

**Postconditions:**

* Alle gespeicherten Produkte werden zurückgegeben

**Verwendet in:**

* GUI-Übersicht
* Reports

---

#### `delete_product(product_id: str) -> None`

Löscht ein Produkt.

**Parameter:**

* `product_id`: eindeutige Produkt-ID

**Preconditions:**

* product_id darf nicht leer sein

**Postconditions:**

* Produkt existiert nicht mehr im Repository

**Exceptions:**

* ValueError: wenn product_id leer ist

**Verhalten:**

* Unbekannte IDs werden ignoriert (kein Fehler)

**Verwendet in:**

* Produkt entfernen

---

#### `save_movement(movement: Movement) -> None`

Speichert eine Lagerbewegung.

**Parameter:**

* `movement`: Movement-Instanz (darf nicht None sein)

**Preconditions:**

* movement.product_id existiert

**Postconditions:**

* Bewegung ist persistent gespeichert

**Exceptions:**

* ValueError: bei ungültiger Bewegung

**Verwendet in:**

* Lagerbestand erhöhen/verringern

---

#### `load_movements() -> List[Movement]`

Lädt alle Lagerbewegungen.

**Return:**

* Liste aller Movement-Objekte

**Postconditions:**

* Alle gespeicherten Bewegungen werden zurückgegeben

**Verwendet in:**

* Bewegungsreport
* Analyse

---

## 2. ReportPort

**Verantwortlich:** Rolle 3 (Reports & Qualität)

### Beschreibung

Abstrakte Schnittstelle zur Generierung von Reports auf Basis gespeicherter Daten.

Reports sind:

* deterministisch
* testbar
* unabhängig von der UI

---

### Methoden

#### `generate_inventory_report() -> str`

Generiert einen Lagerbestandsbericht.

**Inhalt:**

* alle Produkte
* aktueller Bestand
* Gesamtwert pro Produkt

**Return:**

* formatierter String

**Preconditions:**

* Produktdaten vorhanden (kann auch leer sein)

**Postconditions:**

* konsistenter Bericht basierend auf aktuellem Zustand

**Verwendet in:**

* GUI Anzeige
* Report A

---

#### `generate_movement_report() -> str`

Generiert ein Bewegungsprotokoll.

**Inhalt:**

* alle Bewegungen chronologisch
* Menge, Zeit, Benutzer

**Return:**

* formatierter String

**Preconditions:**

* Bewegungsdaten vorhanden (kann leer sein)

**Postconditions:**

* vollständige Historie der Bewegungen

**Verwendet in:**

* GUI Anzeige
* Report B

---

## 3. WarehouseService

**Verantwortlich:** Rolle 2 (Businesslogik)

### Beschreibung

Zentrale Service-Klasse für die Lagerlogik.

---

### Methoden

#### `create_product(...) -> Product`

Erstellt ein neues Produkt.

**Parameter:**

* product_id: str
* name: str
* description: str
* price: float
* category: str (optional)
* initial_quantity: int

**Preconditions:**

* product_id eindeutig
* price >= 0
* initial_quantity >= 0

**Postconditions:**

* Produkt existiert im Repository
* Anfangsbestand gesetzt

**Exceptions:**

* ValueError: bei ungültigen Eingaben

---

#### `add_to_stock(product_id: str, quantity: int, reason: str, user: str) -> None`

Erhöht den Bestand.

**Preconditions:**

* Produkt existiert
* quantity > 0

**Postconditions:**

* Bestand erhöht
* Movement gespeichert

**Exceptions:**

* ValueError: wenn Produkt nicht existiert oder Menge ungültig

---

#### `remove_from_stock(product_id: str, quantity: int, reason: str, user: str) -> None`

Verringert den Bestand.

**Preconditions:**

* Produkt existiert
* quantity > 0
* ausreichend Bestand vorhanden

**Postconditions:**

* Bestand reduziert
* Movement gespeichert

**Exceptions:**

* ValueError: bei unzureichendem Bestand oder ungültigem Produkt

---

#### `get_product(product_id: str) -> Optional[Product]`

**Preconditions:**

* product_id nicht leer

**Return:**

* Product oder None

---

#### `get_all_products() -> Dict[str, Product]`

**Return:**

* alle Produkte

---

#### `get_movements() -> List[Movement]`

**Return:**

* alle Bewegungen

---

#### `get_total_inventory_value() -> float`

Berechnet Gesamtwert des Lagers.

**Postconditions:**

* Summe aller Produktwerte korrekt berechnet

---

## 4. Domain Models

### Product

**Attribute:**

* id: str
* name: str
* description: str
* price: float
* quantity: int
* sku: str
* category: str
* created_at: datetime
* updated_at: datetime
* notes: str

**Regeln (Constraints):**

* id eindeutig
* price >= 0
* quantity >= 0

**Methoden:**

* update_quantity(amount: int) -> None
* get_total_value() -> float

---

### Movement

**Attribute:**

* id: str
* product_id: str
* product_name: str
* quantity_change: int
* movement_type: str ("IN", "OUT", "CORRECTION")
* reason: str
* timestamp: datetime
* performed_by: str

**Regeln:**

* product_id muss existieren
* quantity_change ≠ 0

---

## Versionshistorie der Contracts

### v0.1 (2025-01-20)

* RepositoryPort: CRUD-Operationen definiert
* ReportPort: Basis-Reports
* WarehouseService: Kern-Use-Cases
* Domain Models: Product & Movement

### v0.2

* Preconditions & Postconditions ergänzt
* Fehlerfälle präzisiert
* Use-Case-Bezüge hinzugefügt
