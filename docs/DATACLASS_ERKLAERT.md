# @dataclass ERKLÄRT - Für Old-School Programmierer

## Das Problem: Langweiliger Boilerplate-Code

Die alte Weise (vor Python 3.7):

```python
class Product:
    def __init__(self, id: str, name: str, description: str, price: float, 
                 quantity: int = 0, sku: str = "", category: str = ""):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.sku = sku
        self.category = categorys
    
    def __repr__(self):
        return f"Product(id={self.id!r}, name={self.name!r}, description={self.description!r}, ...)"
    
    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return (self.id == other.id and self.name == other.name and 
                self.description == other.description and self.price == other.price and
                self.quantity == other.quantity and self.sku == other.sku and 
                self.category == other.category)
```

**Viel Code, viel Wiederholung, viel Fehlerquellen!**

---

## Die Lösung: @dataclass (Python 3.7+)

```python
from dataclasses import dataclass

@dataclass
class Product:
    id: str
    name: str
    description: str
    price: float
    quantity: int = 0
    sku: str = ""
    category: str = ""
```

**Das ist alles! Der Rest wird automatisch generiert!**

---

## Was macht @dataclass genau?

### 1️⃣ **Generiert automatisch `__init__()`**

```python
# DU SCHREIBST:
@dataclass
class Product:
    id: str
    name: str
    price: float

# PYTHON GENERIERT AUTOMATISCH:
def __init__(self, id: str, name: str, price: float):
    self.id = id
    self.name = name
    self.price = price
```

**Verwendung:**
```python
product = Product(id="P001", name="Laptop", price=1200.0)
print(product.id)    # Output: P001
print(product.name)  # Output: Laptop
print(product.price) # Output: 1200.0
```

---

### 2️⃣ **Generiert automatisch `__repr__()`**

```python
# PYTHON GENERIERT AUTOMATISCH:
def __repr__(self):
    return f"Product(id='P001', name='Laptop', price=1200.0)"
```

**Verwendung:**
```python
product = Product(id="P001", name="Laptop", price=1200.0)
print(product)  # Output: Product(id='P001', name='Laptop', price=1200.0)
```

---

### 3️⃣ **Generiert automatisch `__eq__()`**

```python
# PYTHON GENERIERT AUTOMATISCH:
def __eq__(self, other):
    if not isinstance(other, Product):
        return NotImplemented
    return (self.id == other.id and self.name == other.name and self.price == other.price)
```

**Verwendung:**
```python
product1 = Product(id="P001", name="Laptop", price=1200.0)
product2 = Product(id="P001", name="Laptop", price=1200.0)
product3 = Product(id="P002", name="Mouse", price=25.0)

print(product1 == product2)  # Output: True (gleiche Werte)
print(product1 == product3)  # Output: False (unterschiedliche Werte)
```

---

## Spezial-Feature: `field()` und `default_factory`

### Problem: Mutable Default Values ⚠️

```python
# FALSCH! (Das würde alle Produkte die gleiche Liste teilen!)
@dataclass
class Product:
    tags: list = []  # DANGER! Alle Instanzen teilen die gleiche Liste!

product1 = Product()
product2 = Product()

product1.tags.append("electronics")
print(product2.tags)  # Output: ['electronics']  ← PROBLEM!
```

### Lösung: `field(default_factory=...)`

```python
from dataclasses import dataclass, field
from datetime import datetime

# RICHTIG! Jede Instanz bekommt ihre eigene Liste
@dataclass
class Product:
    tags: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

product1 = Product()
product2 = Product()

product1.tags.append("electronics")
print(product2.tags)  # Output: []  ← OK! Separate Listes
```

**Warum?**
- `default_factory` ist eine Funktion
- Sie wird **jedes Mal aufgerufen** wenn eine neue Instanz erstellt wird
- Jede Instanz bekommt ihr eigenes Objekt

---

## Spezial-Feature: `__post_init__()`

Nach der automatischen `__init__()` Ausführung kann man `__post_init__()` definieren für zusätzliche Logik:

```python
from dataclasses import dataclass

@dataclass
class Product:
    id: str
    price: float
    
    def __post_init__(self):
        """Wird NACH __init__() automatisch aufgerufen!"""
        if self.price < 0:
            raise ValueError("Preis kann nicht negativ sein")

# Verwendung:
product = Product(id="P001", price=-100)
# ValueError: Preis kann nicht negativ sein
```

**Ablauf:**
1. `__init__(id="P001", price=-100)` wird aufgerufen
2. `self.id = "P001"` und `self.price = -100` werden gesetzt
3. `__post_init__()` wird automatisch aufgerufen
4. Validierung findet statt und ValueError wird geworfen

---

## Vergleich: Alt vs. Neu

### Die alte Weise (pre-3.7)

```python
class Product:
    def __init__(self, id: str, name: str, price: float, quantity: int = 0):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
    
    def __repr__(self):
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r}, quantity={self.quantity!r})"
    
    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return (self.id == other.id and self.name == other.name and 
                self.price == other.price and self.quantity == other.quantity)
    
    def __post_init__(self):
        if not self.id:
            raise ValueError("ID erforderlich")
        if self.price < 0:
            raise ValueError("Preis muss positiv sein")
```

**27 Zeilen Code!**

---

### Die neue Weise (3.7+)

```python
from dataclasses import dataclass

@dataclass
class Product:
    id: str
    name: str
    price: float
    quantity: int = 0
    
    def __post_init__(self):
        if not self.id:
            raise ValueError("ID erforderlich")
        if self.price < 0:
            raise ValueError("Preis muss positiv sein")
```

**11 Zeilen Code!**

---

## Wann sollte man @dataclass verwenden?

| Szenario | @dataclass | Normal Class |
|----------|-----------|--------------|
| Daten-Holder-Klasse (Product, User, etc.) | ✅ JA | ❌ Zu viel Code |
| Komplexe Geschäftslogik | ⚠️ Ja, aber mit mehr Methoden | ✅ JA |
| Factory Pattern | ❌ Nein | ✅ JA |
| Abstract Base Classes | ❌ Nein | ✅ JA |
| Einfache DTO (Data Transfer Object) | ✅ JA | ❌ Overkill |

---

## Schüler/innen Learning Sequence

### Woche 1-2: Verstehen
1. Erklare: "Das @dataclass ist wie ein automatischer Konstruktor-Generator"
2. Zeige: "Wir schreiben nur die Attribute, der Rest wird auto-generiert"
3. Demo: `print(product)` zeigt automatisches `__repr__()`

### Woche 3-4: Deepdive
1. Erkläre: "Warum `field()` mit `default_factory` nötig ist"
2. Demo: Falscher vs. richtiger Default Value
3. Erkläre: "`__post_init__()` für Validierung nach `__init__()`"

### Woche 5+: Vergleich
1. Zeige: "Alte Weise vs. neue Weise"
2. Erkläre: "Warum moderne Python-Code @dataclass nutzt"
3. Diskutiere: "Wann man es verwenden sollte"

---

## Wichtige Punkte für deine Schüler/innen

✅ `@dataclass` ist ein **Decorator** (das `@` Symbol vor der Klasse!)

✅ Es generiert `__init__()`, `__repr__()`, `__eq__()` **automatisch**

✅ **KEIN** Unterschied in der Funktionalität - nur weniger Code zu schreiben!

✅ `field(default_factory=...)` wird verwendet für mutable Defaults

✅ `__post_init__()` wird nach `__init__()` aufgerufen (für Validierung)

❌ **NICHT** verwenden für komplexe Klassen mit viel Business-Logik

---

**TL;DR:** @dataclass = Faulheits-Decorator der dir den `__init__()` schreibt! 😄

