"""App factory para la aplicación Flask."""
from flask import Flask, jsonify

from app.config import get_config
from app.extensions import db, migrate, cors


def create_app() -> Flask:
    """Crea y configura una instancia de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )

    # Importar modelos para que Alembic los detecte
    from app import models  # noqa: F401

    # Blueprints
    from app.routes.simulation import simulation_bp
    from app.routes.application import applications_bp
    app.register_blueprint(simulation_bp)
    app.register_blueprint(applications_bp)

    # Healthcheck
    @app.get("/")
    def root():
        return jsonify({
            "service": "roda-credit-simulator",
            "status": "ok",
            "endpoints": [
                "POST /api/simulate",
                "POST /api/applications",
                "GET  /api/applications",
                "GET  /health",
            ],
        }), 200

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    # Error handler global
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not_found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception(e)
        return jsonify({"error": "internal_server_error"}), 500

    return app