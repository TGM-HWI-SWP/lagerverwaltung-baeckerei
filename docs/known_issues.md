# Known Issues

## Aktuelle Probleme

### Kritisch
- [ ] Keine kritischen Issues momentan

### Hoch
- [ ] [Issue 1 - Beschreibung, Workaround]
- [ ] [Issue 2 - Beschreibung, Workaround]

### Mittel
- [ ] [Issue 1 - Beschreibung]
- [ ] [Issue 2 - Beschreibung]

### Niedrig
- [ ] GUI-Styling könnte verbessert werden
- [ ] [Weitere...]

---

## Gelöste Issues (Archiv)

### v0.1
- ✓ Anfangsproblem bei Repository-Erstellung

### v0.2
- ✓ [Issue] gelöst durch [Lösung]

---

## Bekannte Limitationen

### Features, die absichtlich nicht implementiert sind
- Produktionsreifes Login (nur Demo-Admin im Flask-UI: admin/admin123)
- Persistente Datenbank (Flask-UI currently uses InMemoryRepository)
- Email-Bestellbestätigung
- Mehrsprachigkeit

### Aktuelle Einschränkungen in der neuen Flask GUI
- InMemoryRepository ist flüchtig (neue Startseite setzt Demo-Daten, Daten gehen bei Prozessende verloren)
- Admin-Berechtigungsprüfung ist minimalistisch (kein CSRF, kein OAuth)
- Concurrency / race conditions nicht abgedeckt
- Docker-Compose ist aufgebaut, aber Migration der Demo-Daten in MongoDB erfolgt erst nach Phase 2
- PyQt6 Desktop-App läuft nicht in Docker (fehlende X11/Display) – nutze `.` (lokal) oder `Dockerfile.gui` mit X11-Forwarding


---

## Workarounds

### Issue: [Beschreibung]
**Workaround:** [Beschreibung des Workarounds]

---

**Letzte Aktualisierung:** 2025-01-20
