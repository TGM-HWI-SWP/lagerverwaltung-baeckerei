"""Main entry point for Lagerverwaltung UI.
- Starts Flask web app by default (Docker-compatible)
- To run PyQt6 desktop app locally, use: python -m src.ui.qt_app
"""

from .flask_app import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
