"""Conftest mostruoso: 90 righe di hack per neutralizzare i side-effect.

Ogni patch deve avvenire PRIMA dell'import di app.py, nell'ordine giusto.
Se cambi l'ordine, i test esplodono.
"""

import sys
import types
import threading
import pytest

# === FASE 1: Patch sys.modules per bloccare import pericolosi ===
# Se il codice importasse pymongo o confluent_kafka reali, dovremmo fare:
# sys.modules["pymongo"] = types.ModuleType("pymongo")
# sys.modules["confluent_kafka"] = types.ModuleType("confluent_kafka")
# Per ora il before/ usa classi fake, ma il pattern e' lo stesso.

# Hack 1: Salva il threading.Thread originale
_OriginalThread = threading.Thread


class _NoOpThread:
    """Thread che non parte mai - blocca il consumer daemon."""

    def __init__(self, *args, **kwargs):
        self._target = kwargs.get("target")
        self._daemon = kwargs.get("daemon", False)

    def start(self):
        pass  # Non fare nulla

    def is_alive(self):
        return False

    @property
    def daemon(self):
        return self._daemon

    @daemon.setter
    def daemon(self, value):
        self._daemon = value


# Hack 2: Monkey-patch threading.Thread PRIMA dell'import
threading.Thread = _NoOpThread

# Hack 3: Forza rimozione moduli se gia' importati (ordine critico!)
for mod_name in ["app", "consumer", "services"]:
    if mod_name in sys.modules:
        del sys.modules[mod_name]

# Hack 4: Imposta variabili d'ambiente prima dell'import
import os
os.environ["MONGO_HOST"] = "localhost"
os.environ["MONGO_PORT"] = "27017"
os.environ["KAFKA_BROKERS"] = "localhost:9092"

# Hack 5: Ora possiamo importare (con i side-effect neutralizzati)
import app as app_module  # noqa: E402

# Hack 6: Ripristina threading.Thread per non rompere pytest stesso
threading.Thread = _OriginalThread


# === FASE 2: Fixture ===

@pytest.fixture(autouse=True)
def _reset_state():
    """Reset dello stato globale tra i test.

    Senza questo, i dati inseriti in un test inquinano il successivo.
    Altro hack necessario perche' lo stato e' globale.
    """
    # Pulisci le collections MongoDB fake
    for db_name in list(app_module.mongo_client._databases.keys()):
        db = app_module.mongo_client._databases[db_name]
        for coll_name in list(db._collections.keys()):
            db._collections[coll_name]._docs = []

    # Pulisci i messaggi Kafka
    app_module.kafka_producer._messages = []

    yield


@pytest.fixture
def client():
    """Test client Flask.

    Nota: usa l'app globale, non c'e' modo di crearne una pulita.
    """
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c
