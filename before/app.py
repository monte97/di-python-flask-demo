"""Flask app con side-effect all'import.

Importare questo modulo causa:
- Connessione a MongoDB (localhost:27017)
- Creazione di un KafkaProducer
- Avvio di un thread consumer in background
"""

import threading
from flask import Flask, jsonify, request


# --- Fake MongoDB client (simula pymongo.MongoClient) ---

class FakeCollection:
    def __init__(self):
        self._docs = []

    def find(self, query):
        return list(self._docs)

    def insert_one(self, doc):
        self._docs.append(doc)
        return type("Result", (), {"inserted_id": "fake-id"})()

    def count_documents(self, query):
        return len(self._docs)


class FakeDatabase:
    def __init__(self):
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = FakeCollection()
        return self._collections[name]


class FakeMongoClient:
    """Simula pymongo.MongoClient - in produzione si connetterebbe a localhost:27017."""

    def __init__(self, host="localhost", port=27017):
        self._host = host
        self._port = port
        self._databases = {}
        # Side-effect: tenta connessione reale in produzione
        print(f"[SIDE-EFFECT] MongoClient connecting to {host}:{port}")

    def __getitem__(self, name):
        if name not in self._databases:
            self._databases[name] = FakeDatabase()
        return self._databases[name]


# --- Fake Kafka producer (simula confluent_kafka.Producer) ---

class FakeKafkaProducer:
    """Simula confluent_kafka.Producer - in produzione richiederebbe un broker attivo."""

    def __init__(self, config: dict):
        self._config = config
        self._messages = []
        # Side-effect: tenta connessione al broker
        print(f"[SIDE-EFFECT] KafkaProducer connecting to {config.get('bootstrap.servers')}")

    def produce(self, topic, value=None, **kwargs):
        self._messages.append({"topic": topic, "value": value})

    def flush(self, timeout=None):
        pass


# === SIDE-EFFECTS ALL'IMPORT ===

# 1. Connessione MongoDB
mongo_client = FakeMongoClient("localhost", 27017)

# 2. Creazione Kafka producer
kafka_producer = FakeKafkaProducer({"bootstrap.servers": "localhost:9092"})

# 3. Import del consumer (avvia thread in background)
from consumer import consumer_thread  # noqa: E402


# === FLASK APP ===

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "ok", "consumer_alive": consumer_thread.is_alive()})


@app.route("/users")
def list_users():
    from services import get_all_users
    users = get_all_users()
    return jsonify(users)


@app.route("/events", methods=["POST"])
def create_event():
    from services import publish_event
    data = request.get_json(force=True)
    result = publish_event(data.get("type", "unknown"), data.get("payload", {}))
    return jsonify(result), 201


if __name__ == "__main__":
    app.run(debug=True)
