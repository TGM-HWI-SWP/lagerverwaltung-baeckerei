from .public import public_bp
from .admin import admin_bp


def register_routes(app):
    """Register all Flask blueprints."""
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
