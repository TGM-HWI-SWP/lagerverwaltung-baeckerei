Lagerverwaltungssystem – Bäckerei

Ein teamorientiertes Softwareentwicklungsprojekt zur Umsetzung einer Lagerverwaltungssoftware für eine Bäckerei im Rahmen des Unterrichts Softwareentwicklung & Projektmanagement.

Der Fokus liegt nicht nur auf der Implementierung, sondern vor allem auf professionellen Arbeitsweisen wie Architektur, Versionierung, Testing und Dokumentation.

Projektziel

Ziel ist die Entwicklung einer Anwendung zur Verwaltung von Produkten, Lagerständen und Bewegungen in einer Bäckerei.

Dabei werden folgende Aspekte umgesetzt:

Verwaltung von Produkten und Lagerbeständen
Nachverfolgung von Lagerbewegungen
Generierung von Reports (z. B. Lagerstand, Bewegungen)
GUI zur Benutzerinteraktion
Persistente Datenspeicherung
Testbare und modular aufgebaute Software
Projektfokus (Wichtig!)

Rollenverteilung: 
Rolle 1 (Projektverantwortung und Schnittstellen): Zwanzinger Luis
Rolle 2 (Bsuinesslogik und Report A): Theussl Felix 
Rolle 3 (Report B und Qualität): Seibert Laurin 
Rolle 4 (GUI und Interaktion): Wippelk Sofia

Architektur

Das Projekt basiert auf dem Port-/Adapter-Prinzip (Hexagonale Architektur):

                +----------------------+
                |        UI            |
                | (Qt / Flask)         |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      Services        |
                |  (Business Logic)    |
                +----------+-----------+
                           |
        +------------------+------------------+
        |                                     |
        v                                     v
+---------------------+           +----------------------+
|        Ports        |           |       Reports        |
| (Interfaces)        |           | (Auswertungen)       |
+----------+----------+           +----------+-----------+
           |                                 |
           v                                 v
+---------------------+           +----------------------+
|      Adapters       |           |   Report-Adapter     |
| (DB, InMemory, etc) |           |                      |
+---------------------+           +----------------------+

Projektstruktur
.
├── src/
│   ├── domain/        # Fachlogik (Produkte, Lager)
│   ├── services/      # Businesslogik
│   ├── ports/         # Schnittstellen (Interfaces)
│   ├── adapters/      # Implementierungen (DB, Reports)
│   ├── reports/       # Report-Logik
│   └── ui/            # GUI (Qt / Flask)
│
├── docs/              # Projektdokumentation
├── tests/             # Unit- & Integrationstests
├── pyproject.toml     # Projektkonfiguration
├── docker-compose.yml # Container Setup
└── README.md
Setup & Start
1. Repository klonen
git clone <repo-url>
cd lagerverwaltung-baeckerei
2. Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
3. Abhängigkeiten installieren
pip install -e .
▶Anwendung starten
GUI mit Docker starten
docker-compose up --build
Tests ausführen
pytest

Getestet werden:

Domain-Logik
Businesslogik
Reports (Berechnungen)
Reports

Die Reports sind eigenständige Komponenten und bieten z. B.:

Lagerstandsübersicht
Bewegungsprotokoll
Grafische Auswertungen (z. B. mit matplotlib)

Wichtig: Tests prüfen Daten, nicht das Layout!

Dokumentation

Wichtige Dokumente im Projekt:

docs/contracts.md → Schnittstellen (zentral!)
docs/architecture.md → Systemaufbau
docs/tests.md → Teststrategie
docs/retrospective.md → Reflexion
docs/changelog_<name>.md → Individuelle Beiträge
Git & Zusammenarbeit
Arbeiten mit Branches
Regelmäßige Commits
Umgang mit Mergekonflikten
Versionierung über Tags (v0.x → v1.0)

## Known Issues

Siehe `docs/known_issues.md`

## Lizenz

Schulprojekt - TGM