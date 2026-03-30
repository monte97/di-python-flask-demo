"""Test dell'after/ - assertion forti, mock iniettati.

Ogni test verifica il contenuto della risposta e gli effetti collaterali
registrati nei mock. Il mutation testing non riesce a passare inosservato.
"""

import json
from services import UserService, EventService


def test_index(client):
    response = client.get("/")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "ok"


def test_list_users_empty(client):
    response = client.get("/users")
    data = response.get_json()
    assert response.status_code == 200
    assert data == []


def test_list_users_with_data(client, mock_db):
    mock_db.stored.append({"_collection": "users", "name": "Alice"})
    mock_db.stored.append({"_collection": "users", "name": "Bob"})

    response = client.get("/users")
    data = response.get_json()

    assert len(data) == 2
    assert data[0]["name"] == "Alice"
    assert data[1]["name"] == "Bob"


def test_list_users_missing_name(client, mock_db):
    mock_db.stored.append({"_collection": "users"})

    response = client.get("/users")
    data = response.get_json()

    assert len(data) == 1
    assert data[0]["name"] == "unknown"


def test_create_event(client, mock_producer):
    response = client.post(
        "/events",
        data=json.dumps({"type": "user.created", "payload": {"user": "Bob"}}),
        content_type="application/json",
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["type"] == "user.created"
    assert data["data"]["user"] == "Bob"

    # Verifica che l'evento sia stato inviato al producer
    assert len(mock_producer.sent) == 1
    assert mock_producer.sent[0]["topic"] == "events"
    assert mock_producer.sent[0]["value"]["type"] == "user.created"


def test_create_event_default_type(client, mock_producer):
    response = client.post(
        "/events",
        data=json.dumps({"payload": {"user": "Charlie"}}),
        content_type="application/json",
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["type"] == "unknown"

    assert len(mock_producer.sent) == 1
    assert mock_producer.sent[0]["value"]["type"] == "unknown"


def test_user_count(mock_db):
    """Test diretto sul service - possibile grazie alla DI."""
    mock_db.stored.append({"_collection": "users", "name": "Alice"})
    mock_db.stored.append({"_collection": "users", "name": "Bob"})

    service = UserService(db=mock_db)
    assert service.get_user_count() == 2


def test_user_count_empty(mock_db):
    service = UserService(db=mock_db)
    assert service.get_user_count() == 0
