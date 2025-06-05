.PHONY: test-unit
test-unit:
	python3 -m unittest discover -v -s tests

.PHONY: build
build:
	uv sync --extra build
	uv build