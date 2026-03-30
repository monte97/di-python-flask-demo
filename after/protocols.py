"""Protocol classes per le dipendenze.

Definiscono i contratti senza legare il codice a implementazioni concrete.
"""

from typing import Protocol


class DatabaseClient(Protocol):
    def find(self, collection: str, query: dict) -> list: ...
    def insert(self, collection: str, doc: dict) -> str: ...
    def count(self, collection: str, query: dict) -> int: ...


class EventProducer(Protocol):
    def send(self, topic: str, value: dict) -> None: ...
