"""Test del before/ - funzionano solo grazie al conftest mostruoso.

Assertion deboli: verificano solo lo status code, non il contenuto.
Il mutation testing li punira'.
"""

import json


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_list_users_empty(client):
    response = client.get("/users")
    assert response.status_code == 200


def test_list_users_with_data(client):
    # Inserisci dati direttamente nel client globale (altro accoppiamento)
    import app as app_module

    app_module.mongo_client["mydb"]["users"]._docs.append({"name": "Alice"})

    response = client.get("/users")
    assert response.status_code == 200


def test_create_event(client):
    response = client.post(
        "/events",
        data=json.dumps({"type": "user.created", "payload": {"user": "Bob"}}),
        content_type="application/json",
    )
    assert response.status_code == 201


def test_create_event_default_type(client):
    response = client.post(
        "/events",
        data=json.dumps({"payload": {"user": "Charlie"}}),
        content_type="application/json",
    )
    assert response.status_code == 201
