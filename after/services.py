"""Business logic con constructor injection.

Nessuna dipendenza globale, nessun import di client concreti.
Le dipendenze arrivano dal chiamante.
"""

from protocols import DatabaseClient, EventProducer


class UserService:
    def __init__(self, db: DatabaseClient):
        self._db = db

    def get_all_users(self) -> list[dict]:
        users = self._db.find("users", {})
        return [{"name": u.get("name", "unknown")} for u in users]

    def get_user_count(self) -> int:
        return self._db.count("users", {})


class EventService:
    def __init__(self, producer: EventProducer):
        self._producer = producer

    def publish_event(self, event_type: str, payload: dict) -> dict:
        message = {"type": event_type, "data": payload}
        self._producer.send("events", message)
        return message
