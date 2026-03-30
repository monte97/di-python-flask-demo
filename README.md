# DI in Python: da side-effect all'import a application factory

Repo demo che mostra il refactoring da codice Flask con side-effect all'import (MongoClient, KafkaProducer, thread consumer che partono al `import app`) a dependency injection con application factory. Il mutation testing misura la differenza nella qualita' dei test.

## Quick start

```bash
make install
make demo
```

## Cosa confronta

| Metrica | before/ | after/ |
|---------|---------|--------|
| Righe conftest | ~90 | ~30 |
| Hack (sys.modules, monkey-patch) | 6 | 0 |
| Side-effect all'import | 3 (Mongo, Kafka, thread) | 0 |
| Assertion nei test | deboli (solo status code) | forti (contenuto + effetti) |
| Mutation score (`services.py`) | 14% (2/14) | 100% (12/12) |

## Struttura

```
before/   -- Flask app con stato globale e side-effect
after/    -- Application factory + Protocol + constructor injection
```

## Comandi

```bash
make test-before     # Esegue test before/
make test-after      # Esegue test after/
make mutate-before   # Mutation testing su before/services.py
make mutate-after    # Mutation testing su after/services.py
make clean           # Rimuove cache
```

## Requisiti

- Python 3.10+
- `pip install -r requirements.txt` (Flask, pytest, mutmut 2.x)

Nessuna dipendenza esterna (pymongo, confluent-kafka): il before/ simula i client con classi fake per isolare il punto del demo.

## Riferimenti

- Post LinkedIn: <!-- TODO: inserire URL -->
- Articolo completo: <!-- TODO: inserire URL montelli.dev -->
