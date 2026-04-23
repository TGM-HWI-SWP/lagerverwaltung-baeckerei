# Changelog - [ZwanzingerLuis]

Persönliches Changelog für [ZwanzingerLuis], Rolle: [Rolle1]

---

## [v0.1] - 20.03.2026

### Implementiert
- Dummy Daten
- Changelogs hinzugefügt


### Mergekonflikt(e)
- [Problem] Beim Pullen und commiten gab es fehler, da der Name des Projektes geändert wurde.
- [Lösung] In [lagerverwaltung-backerei\.git\config] den Namen korrigieren und mit: [git pull --allow-unrelated-histories] richtig pullen. 
---

## [v0.2] - [27.03.2026]

### Implementiert
- Unterstützung der Mitarbeiter
    - helfen Docker Desktop zum laufen zu bringen
    - helfen beim commiten 
    - bei import problemen geholfen in test_movement.py
- gui getestet


### Mergekonflikt(e)
- Keine

---

## [v0.3] - [17.04.2026]

### Implementiert
- **product_list.html dynamische Integration:**
  - Vorher: Hardcodierte Produkte im HTML
  - Nachher: Dynamisch aus `dummy_data.json`
  - Placeholder-Bilder mit dynamischen Produktnamen
  - Darstellung bleibt unverändert


### Probleme & Lösungen
- **Problem:** MongoDB persistiert Daten zwischen Restarts → JSON nicht neu geladen
  - **Lösung:** `docker compose down -v` löscht alle Volumes, DB wird beim Start gefüllt
  
- **Problem:** Debug-Messages waren nicht sichtbar
  - **Lösung:** print() in Flask schreibt in Container-Logs, `docker compose logs -f` zeigt diese

### Commits
```
- Feat: product_list.html dynamisch aus dummy_data.json
- Feat: _init_demo_data() JSON-Integration mit Fallback
- Feat: Debug-Ausgaben für Datenladen und Pfadtracking
- Docs: contracts.md MongoRepository dokumentiert
```

### Mergekonflikt(e)
- Keine

---

## [v0.4] - [23.04.2026]

### Implementiert
- Überarbeitung von contracts.md auf professionelles Niveau:
  - Ergänzung von Preconditions & Postconditions für zentrale Service-Methoden
  - Erweiterung der Fehlerfall-Definitionen (Exceptions)
  - Einführung von Use-Case-Bezügen („Verwendet in“) zur besseren Nachvollziehbarkeit
  - Ergänzung von Constraints/Regeln bei Domain Models (z. B. price ≥ 0, quantity ≥ 0)
  - Präzisere Beschreibung der Repository- und Report-Schnittstellen
  - Verbesserung der Struktur und Klarheit der Dokumentation
- Fokus auf bewertungsrelevante Aspekte:
  - Testbarkeit
  - Nachvollziehbarkeit
  - klare Schnittstellendefinition
### Probleme & Lösungen
  - Problem: Contracts waren funktional korrekt, aber zu oberflächlich für eine sehr gute Bewertung
  - Lösung: Erweiterung um formale Spezifikationen (Pre/Postconditions, Constraints)
  - Problem: Fehlende Verbindung zwischen Methoden und Use-Cases
  - Lösung: Einführung von „Verwendet in“-Abschnitten
### Commits
  - Docs: contracts.md um Preconditions & Postconditions erweitert
  - Docs: Fehlerfälle und Constraints ergänzt
  - Docs: Use-Case-Bezüge hinzugefügt
  - Docs: Struktur und Lesbarkeit verbessert

### Mergekonflikt(e)
  Keine
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
