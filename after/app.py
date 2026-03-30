"""Application factory Flask con dependency injection.

Nessun side-effect all'import. I client vengono iniettati via config dict.
"""

from flask import Flask, jsonify, request
from services import UserService, EventService


def create_app(config: dict) -> Flask:
    """Crea l'app Flask con le dipendenze iniettate.

    Args:
        config: dict con chiavi "db" (DatabaseClient) e "producer" (EventProducer).
    """
    app = Flask(__name__)

    user_service = UserService(db=config["db"])
    event_service = EventService(producer=config["producer"])

    @app.route("/")
    def index():
        return jsonify({"status": "ok"})

    @app.route("/users")
    def list_users():
        users = user_service.get_all_users()
        return jsonify(users)

    @app.route("/events", methods=["POST"])
    def create_event():
        data = request.get_json(force=True)
        result = event_service.publish_event(
            data.get("type", "unknown"),
            data.get("payload", {}),
        )
        return jsonify(result), 201

    return app
