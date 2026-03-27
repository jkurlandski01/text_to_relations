# Declaring 'build' as phony ensures 'make build' always runs, even if a file named 'build' exists.
.PHONY: build
build:
	# Remove old builds before creating new ones.
	rm -rf dist/
	python -m build
