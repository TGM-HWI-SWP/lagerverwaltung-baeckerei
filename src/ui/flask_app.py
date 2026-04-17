import os
from flask import Flask

from .routes import register_routes


def create_app(test_config=None):
    """Flask application factory for Lagerverwaltung GUI."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    if test_config is not None:
        app.config.update(test_config)

    register_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
