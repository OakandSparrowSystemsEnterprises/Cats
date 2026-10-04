# Tetra build: maps -> check -> page -> tests. Each target can be run on its own.
.PHONY: all maps check build test seams audit clean
all: maps build test audit
maps:
	cd pipeline && python3 mapgen2.py
check:
	cd pipeline && python3 check_edges.py
build:
	python3 pipeline/build.py
test: build
	node tests/smoke.js && node tests/walkthrough.js && node tests/phases.js && node tests/calendar.js && node tests/cuba.js && node tests/tap.js
seams: build
	node tests/seams.js
audit:
	python3 tools/audit.py
clean:
	rm -rf tests/out pipeline/__pycache__
