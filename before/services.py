"""Business logic accoppiata ai client globali."""


def get_all_users():
    """Recupera tutti gli utenti da MongoDB."""
    from app import mongo_client

    db = mongo_client["mydb"]
    users = list(db["users"].find({}))
    return [{"name": u.get("name", "unknown")} for u in users]


def publish_event(event_type: str, payload: dict):
    """Pubblica un evento su Kafka."""
    from app import kafka_producer

    message = {"type": event_type, "data": payload}
    kafka_producer.produce("events", value=message)
    kafka_producer.flush()
    return message


def get_user_count():
    """Conta gli utenti nel database."""
    from app import mongo_client

    db = mongo_client["mydb"]
    return db["users"].count_documents({})
