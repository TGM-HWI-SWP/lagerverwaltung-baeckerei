# Architektur-Dokumentation

## Architektur-Übersicht

Das Projekt folgt der **Port-Adapter-Architektur** (Hexagonal Architecture) mit Unterstützung für mehrere UI-Optionen (Web + Desktop).

## Dependency-Struktur (pyproject.toml)

### Basis-Dependencies (immer erforderlich)
- `Flask>=2.3.0` – Web-Framework
- `pymongo>=4.7.0` – MongoDB-Treiber
- `tinydb>=4.8.0` – Alternative In-Memory DB

### Optional: `[gui]`
- `PyQt6>=6.6.0` – Desktop-GUI (Qt6)
- **Nur für lokale native App nötig, nicht für Docker Web-Container**

### Optional: `[web]`
- Beinhaltet `Flask`, `pymongo`, `pytest`
- Für Docker Compose & Web-Betrieb

### Optional: `[dev]`
- Linting, Testing, Type Checking

## Schichten-Modell

```
┌─────────────────────────────────────────────────────────┐
│                    UI-Layer (PyQt6)                     │
│              WarehouseMainWindow, Dialoge               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Service-Layer                          │
│              WarehouseService, BusinessLogic            │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Domain-Layer                           │
│          Product, Movement, Warehouse (Entities)        │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌────────▼──────────┐
│  Ports         │          │   Adapters       │
│  (Abstract)    │          │ (Implementations)│
│                │          │                   │
│RepositoryPort │◄────────►│InMemoryRepository│
│ ReportPort     │          │(sqlite, json, ...|
└────────────────┘          └───────────────────┘
```

## Komponenten

### 1. Domain Layer (`src/domain/`)

**Verantwortung:** Reine Geschäftslogik, unabhängig von technischen Details

#### `product.py`
- **Klasse:** `Product`
- **Attribute:** id, name, description, price, quantity, sku, category, created_at, updated_at, notes
- **Methoden:**
  - `update_quantity(amount)` - Bestand aktualisieren mit Validierung
  - `get_total_value()` - Lagerwert berechnen
- **Validierung:** Negative Preise/Bestände nicht erlaubt

#### `warehouse.py`
- **Klasse:** `Warehouse`
  - **Attribute:** name, products (Dict), movements (List)
  - **Methoden:**
    - `add_product(product)` - Produkt hinzufügen
    - `get_product(id)` - Produkt abrufen
    - `record_movement(movement)` - Bewegung protokollieren
    - `get_total_inventory_value()` - Gesamtwert
    - `get_inventory_report()` - Report-Daten

- **Klasse:** `Movement`
  - **Attribute:** id, product_id, product_name, quantity_change, movement_type, reason, timestamp, performed_by
  - **Beschreibung:** Immutable Bewegungslog

### 2. Ports (`src/ports/`)

**Verantwortung:** Schnittstellen-Definitionen (Abstraktion)

#### `RepositoryPort`
```python
class RepositoryPort(ABC):
    @abstractmethod
    def save_product(self, product: Product) -> None: ...
    
    @abstractmethod
    def load_product(self, product_id: str) -> Optional[Product]: ...
    
    @abstractmethod
    def load_all_products(self) -> Dict[str, Product]: ...
    
    @abstractmethod
    def delete_product(self, product_id: str) -> None: ...
    
    @abstractmethod
    def save_movement(self, movement: Movement) -> None: ...
    
    @abstractmethod
    def load_movements(self) -> List[Movement]: ...
```

#### `ReportPort`
```python
class ReportPort(ABC):
    @abstractmethod
    def generate_inventory_report(self) -> str: ...
    
    @abstractmethod
    def generate_movement_report(self) -> str: ...
```

### 3. Adapters (`src/adapters/`)

**Verantwortung:** Konkrete Implementierungen der Ports

#### `repository.py`

**InMemoryRepository**
- **Ziel:** Schnell, für Tests und Prototyping
- **Speicher:** In RAM (Dict, List)
- **Performance:** O(1) für Zugriff
- **Persistenz:** Nein

**RepositoryFactory**
- **Pattern:** Factory Pattern
- **Methode:** `create_repository(type: str) -> RepositoryPort`
- **Typen:** "memory" (weitere später)

#### `report.py`

**ConsoleReportAdapter**
- **Ziel:** Text-basierte Report-Generierung
- **Ausgabe:** Formatierte Strings
- **Verwendung:** Console, Logging, Dateiexport

### 4. Services (`src/services/`)

**Verantwortung:** Business-Use-Cases, Orchestrierung

#### `WarehouseService`
- **Dependency Injection:** Repository über Constructor
- **Methoden:**
  - `create_product(...)` - Neues Produkt
  - `add_to_stock(product_id, quantity, reason, user)` - Bestand erhöhen
  - `remove_from_stock(product_id, quantity, reason, user)` - Bestand verringern
  - `get_product(product_id)` - Produkt abrufen
  - `get_all_products()` - Alle Produkte
  - `get_movements()` - Alle Bewegungen
  - `get_total_inventory_value()` - Gesamtwert

### 5. UI Layer (`src/ui/`)

**Verantwortung:** Benutzeroberfläche (PyQt6 + Flask)

#### `WarehouseMainWindow` (PyQt6)
- **Framework:** PyQt6
- **Layout:** Tab-basiert
  - Tab 1: Produktverwaltung (Tabelle, Buttons)
  - Tab 2: Lagerbewegungen (Protokoll)
  - Tab 3: Berichte (Report-Generierung)

#### `ProductDialogWindow`
- **Typ:** Modal Dialog
- **Felder:** ID, Name, Beschreibung, Preis, Menge, Kategorie

#### `src/ui/flask_app.py` und `src/ui/routes/`
- **Typ:** Web-UI (Flask)
- **Routen:** Startseite, Über uns, Produktübersicht, Produktdetail, Bestellprozess, Admin-Login, Dashboard, Bestellübersicht, Lagerbestand, Statistik
- **Templating:** Jinja2 unter `src/ui/templates/`
- **Static Assets:** CSS unter `src/ui/static/css/style.css`
- **Service-Anbindung:** `WarehouseService` über `RepositoryFactory.create_repository('memory')` (für v0.1 als InMemory-Placeholder)

### 6. Tests (`tests/`)

#### Unit Tests (`tests/unit/`)
```
test_domain.py
  - TestProduct
    - test_product_creation
    - test_product_validation_*
    - test_update_quantity*
    - test_get_total_value
  
  - TestWarehouseService
    - test_create_product
    - test_add_to_stock
    - test_remove_from_stock*
    - test_get_all_products
    - test_get_total_inventory_value
    - test_get_movements
```

#### Integration Tests (`tests/integration/`)
```
test_integration.py
  - TestIntegration
    - test_full_workflow
    - test_report_generation
```

## Dependency Injection

```python
# Beispiel:
repository = RepositoryFactory.create_repository("memory")
service = WarehouseService(repository)
ui = WarehouseMainWindow()
```

**Vorteile:**
- Lose Kopplung
- Einfaches Testen (Mock-Repositories)
- Austauschbare Implementierungen

## Datenflusss

```
UI-Ereignis
    ↓
Service-Methode (WarehouseService)
    ↓
Domain-Validierung (Product.update_quantity)
    ↓
Repository-Operation (save_product, save_movement)
    ↓
Speicherung (InMemory, später SQLite, JSON, etc.)
    ↓
Rückmeldung an UI
```

## Erweiterungen (Roadmap)

### SQLite-Adapter
```python
class SQLiteRepository(RepositoryPort):
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def save_product(self, product: Product) -> None:
        # SQL-INSERT oder UPDATE
        pass
```

### JSON-Adapter
```python
class JSONRepository(RepositoryPort):
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def save_product(self, product: Product) -> None:
        # JSON-Serialisierung
        pass
```

### Grafik-Reports
```python
class MatplotlibReportAdapter(ReportPort):
    def generate_inventory_report(self) -> str:
        # Matplotlib-Diagramme
        pass
```

## Testing-Strategie

### Unit Tests
- Domäne isoliert testen
- Mock-Repository verwenden
- Fokus auf Geschäftslogik

### Integration Tests
- Komponenten zusammen testen
- Real Service + Real Repository
- Komplette Workflows

### Datengenerierung
Dummy-Daten für Tests:
```python
service.create_product("TEST-001", "Test Product", "Test", 100.0, initial_quantity=50)
```

## Performance-Überlegungen

### Aktuell (In-Memory)
- Alle Operationen: O(1) bis O(n)
- Speicher: Begrenzt durch RAM
- Ideal für: Prototyping, Tests

### Zukünftig (Datenbank)
- Indizes für häufige Abfragen
- Pagginierung für große Datenmengen
- Connection Pooling

## Sicherheit (Roadmap)

- Benutzer-Authentifizierung
- Audit-Logging für Änderungen
- Validierung aller Eingaben
- SQL-Injection-Schutz (bei DBs)

## Dokumentation

- Schnittstellen: `docs/contracts.md`
- Architektur: `docs/architecture.md`
- Tests: `docs/tests.md`
- Changelog: `docs/changelog_<name>.md`

---

**Letzte Aktualisierung:** 2025-01-20
**Version:** 0.1
