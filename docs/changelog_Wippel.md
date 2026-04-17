# Changelog - [Sofia Wippel]

Persönliches Changelog für [Sofia Wippel], Rolle: [GUI & Interaktion ]

---

## [v0.1] - 2026-03-27

### Implementiert
- GUI Grundgerüst mit Flask und Qt
- Docker Container Setup
- Verlinkungen zwischen den Seiten
- Responsive Design mit CSS
- Admin Dashboard Struktur
- Produktverwaltung UI

### Tests geschrieben
- Noch keine Tests geschrieben

### Commits
```
- ede7975 Feat: Grundgerüst der GUI fertig inkl. laufendem Docker
```

### Mergekonflikt(e)
- README.md: Merge Konflikt gelöst

---

## [v0.2] - 2026-04-17

### Implementiert
- Reparatur des Admin Logins
- Neues Design der GUI
- Integration von Dummy-Daten in product_list.html
- Tests für Movement-Klasse und MovementReport
- Integrationstests für den kompletten Workflow (Produkterstellung, Lagerbewegungen, Berichterstellung)

### Tests geschrieben
- test_movement_report.py (Unit-Tests für Movement und MovementReport)
- test_integration.py (Integrationstests für vollständigen Workflow)

### Commits
```
- 55eb677 product list.html benutzt jetzt die dummy daten
- 80adecc Admin login repariert
- fe3a6a6 neues design der gui
- ee5ee8d Movment class implementierung sowie eine Test Datei
```

### Mergekonflikt(e)
- Keine

---

## [v0.3] - 2026-04-17 (Einheit 3 - MongoDB & Docker Integration)

### Implementiert
- **MongoDB Integration**: MongoDB als primäres Produktions-Repository eingeführt
- **Seed-Skript**: `seed_mongo.py` erstellt, das Dummy-Daten aus `tests/dummy_data.json` einmalig in MongoDB einfügt
- **Ein-malige Vorladung**: `docker-compose.yml` so angepasst, dass beim Container-Start automatisch der Seed ausgeführt wird
- **Error Handling & Fallback**: Bei MongoDB-Ausfall fällt System auf In-Memory-Daten aus JSON zurück
- **Produktdaten erweitert**: Produkten-Domain mit `image`-Feld ergänzt für Platzhalterbilder
- **Docker-Compose Vereinfachung**: Auf 2 Services optimiert (MongoDB + Flask-App statt 3)
- **Swagger UI Integration**: Flasgger in Flask konfiguriert für API-Dokumentation unter `/apidocs`
- **Import-Bug gefixt**: Fehlende `Optional` und `os`-Imports in `repository.py` behoben

### Zugänge & Ports
- **Flask GUI**: `http://localhost:5000`
- **Swagger UI (API-Docs)**: `http://localhost:5000/apidocs`
- **MongoDB (intern)**: `mongodb://mongo:27017/` (im Docker-Netzwerk)

### Tests geschrieben
- Keine neuen Tests; bestehende Tests weiterhin gültig

### Commits & Änderungen
```
- seed_mongo.py erstellt
- docker-compose.yml angepasst (2 Services: mongo + app)
- src/adapters/repository.py: Imports ergänzt (Optional, os, typing)
- src/adapters/mongo_repository.py: Alle Produktfelder (image, sku, etc.) unterstützt
- src/domain/product.py: image-Feld hinzugefügt
- src/ui/flask_app.py: Swagger/Flasgger konfiguriert
- tests/dummy_data.json: image-Platzhalter für alle Produkte
```

### Mergekonflikt(e)
- Keine

---

## [v0.4] - [Datum]

### Implementiert
- [Feature/Fix]

### Tests geschrieben
- [Tests]

### Commits
```
- [Commits]
```

### Mergekonflikt(e)
- [Konflikte]

---

## [v0.5] - [Datum]

### Implementiert
- [Feature/Fix]

### Tests geschrieben
- [Tests]

### Commits
```
- [Commits]
```

### Mergekonflikt(e)
- [Konflikte]

---

## [v1.0] - [Datum]

### Implementiert
- [Feature/Fix]

### Tests geschrieben
- [Tests]

### Commits
```
- [Commits]
```

### Mergekonflikt(e)
- [Konflikte]

---

## Zusammenfassung

**Gesamt implementierte Features:** [Anzahl]  
**Gesamt geschriebene Tests:** [Anzahl]  
**Gesamt Commits:** [Anzahl]  
**Größte Herausforderung:** [Beschreibung]  
**Schönste Code-Zeile:** [Code-Snippet]

---

**Changelog erstellt von:** [Name]  
**Letzte Aktualisierung:** [Datum]
