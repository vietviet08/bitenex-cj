COMPOSE_FILE := infra/docker-compose/docker-compose.yml

up:
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

migrate:
	@echo "TODO: add Alembic migrations"
