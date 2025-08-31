.PHONY: up down logs test fmt lint

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f

test:
	docker compose run --rm api pytest -q
