"""Conftest pulito: mock iniettati, nessun hack.

~50 righe vs ~90 del before. Zero sys.modules, zero monkey-patch.
"""

import pytest
from app import create_app


class MockDB:
    def __init__(self):
        self.stored = []

    def find(self, collection, query):
        return [d for d in self.stored if d.get("_collection") == collection]

    def insert(self, collection, doc):
        doc["_collection"] = collection
        self.stored.append(doc)
        return "mock-id"

    def count(self, collection, query):
        return len([d for d in self.stored if d.get("_collection") == collection])


class MockProducer:
    def __init__(self):
        self.sent = []

    def send(self, topic, value):
        self.sent.append({"topic": topic, "value": value})


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def mock_producer():
    return MockProducer()


@pytest.fixture
def client(mock_db, mock_producer):
    app = create_app({"db": mock_db, "producer": mock_producer})
    app.config["TESTING"] = True
    return app.test_client()
