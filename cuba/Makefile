.PHONY: maps build test audit
maps:
	cd pipeline && python3 mapgen.py
build:
	python3 pipeline/build.py
test: build
	node tests/smoke.js
audit:
	python3 tools/audit.py
