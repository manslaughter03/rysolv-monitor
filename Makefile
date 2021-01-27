.PHONY: lint build

lint:
	tox -e pylint

build:
	docker-compose build
