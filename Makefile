.PHONY: test-before test-after mutate-before mutate-after clean demo install

install:
	pip install -r requirements.txt -q

test-before:
	cd before && python -m pytest test_app.py -v -p no:flask

test-after:
	cd after && python -m pytest test_app.py -v -p no:flask

mutate-before:
	cd before && rm -rf .mutmut-cache && mutmut run --paths-to-mutate=services.py --tests-dir=. --no-progress 2>/dev/null; \
	python3 -c "import sqlite3; from collections import Counter; \
	conn = sqlite3.connect('.mutmut-cache'); c = conn.cursor(); \
	c.execute('SELECT status FROM Mutant'); rows = c.fetchall(); \
	s = Counter(r[0] for r in rows); t = len(rows); k = s.get('ok_killed', 0); \
	print(f'\n=== BEFORE: mutation score {k*100//t}% ({k}/{t} killed) ===')"

mutate-after:
	cd after && rm -rf .mutmut-cache && mutmut run --paths-to-mutate=services.py --tests-dir=. --no-progress 2>/dev/null; \
	python3 -c "import sqlite3; from collections import Counter; \
	conn = sqlite3.connect('.mutmut-cache'); c = conn.cursor(); \
	c.execute('SELECT status FROM Mutant'); rows = c.fetchall(); \
	s = Counter(r[0] for r in rows); t = len(rows); k = s.get('ok_killed', 0); \
	print(f'\n=== AFTER: mutation score {k*100//t}% ({k}/{t} killed) ===')"

demo: test-before test-after mutate-before mutate-after

clean:
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null; find . -name ".mutmut-cache" -exec rm -rf {} + 2>/dev/null; find . -name "mutants" -exec rm -rf {} + 2>/dev/null
