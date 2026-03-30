"""Kafka consumer che parte come thread daemon all'import."""

import threading
import time

_running = True


def _consume_loop():
    """Loop di consumo Kafka simulato - gira in background."""
    while _running:
        # Simula polling da Kafka
        time.sleep(1.0)


# Side-effect: il thread parte appena qualcuno importa questo modulo
consumer_thread = threading.Thread(target=_consume_loop, daemon=True)
consumer_thread.start()
