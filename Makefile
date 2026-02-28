.DEFAULT_GOAL := help
COMPOSE := docker compose

# ──────────────────────────────────────────────
# Docker lifecycle
# ──────────────────────────────────────────────

.PHONY: up down rebuild logs

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

rebuild: ## Rebuild images and restart
	$(COMPOSE) up -d --build

logs: ## Tail logs (all services)
	$(COMPOSE) logs -f

# ──────────────────────────────────────────────
# Django management (runs inside web container)
# ──────────────────────────────────────────────

.PHONY: shell dbshell migrate makemigrations createsuperuser collectstatic

shell: ## Open Django shell
	$(COMPOSE) exec web python manage.py shell

dbshell: ## Open database shell
	$(COMPOSE) exec db psql -U mediacms mediacms

migrate: ## Run Django migrations
	$(COMPOSE) exec web python manage.py migrate

makemigrations: ## Create new migrations
	$(COMPOSE) exec web python manage.py makemigrations

createsuperuser: ## Create admin superuser
	$(COMPOSE) exec web python manage.py createsuperuser

collectstatic: ## Collect static files
	$(COMPOSE) exec web python manage.py collectstatic --noinput

# ──────────────────────────────────────────────
# Quality gates
# ──────────────────────────────────────────────

.PHONY: test lint format format-check check

test: ## Run pytest inside web container
	$(COMPOSE) exec -e TESTING=True web pytest

lint: ## Run flake8 inside web container
	$(COMPOSE) exec web flake8

format: ## Run black (auto-fix) inside web container
	$(COMPOSE) exec web black .

format-check: ## Check formatting without changing files
	$(COMPOSE) exec web black --check .

check: lint format-check test ## Run all quality gates (lint + format-check + test)

# ──────────────────────────────────────────────
# Remote sync (mirror bjj.chadao.ro content)
# ──────────────────────────────────────────────

REMOTE_HOST ?= bjj.chadao.ro
REMOTE_USER ?= root
REMOTE_DIR  ?= /mediacms/cms/mediacms
REMOTE_COMPOSE ?= docker-compose-letsencrypt.yaml

.PHONY: sync-db sync-assets sync-remote

sync-db: ## Dump remote DB and restore locally
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T db pg_dump -U mediacms -Fc mediacms" > bjj_dump.pgdump
	$(COMPOSE) exec -T db pg_restore -U mediacms -d mediacms --clean --if-exists < bjj_dump.pgdump
	@echo "Database restored. Run 'make migrate' if needed."

sync-assets: ## Download thumbnails + HLS manifests from remote
	$(COMPOSE) exec web python manage.py sync_remote_assets

sync-remote: sync-db sync-assets ## Full sync: database + assets from remote

# ──────────────────────────────────────────────
# Status
# ──────────────────────────────────────────────

.PHONY: status

status: ## Show running containers and URLs
	@echo "=== Running containers ==="
	@$(COMPOSE) ps
	@echo ""
	@echo "=== URLs ==="
	@echo "  Web:     http://localhost"
	@echo "  API:     http://localhost/api/v1/"
	@echo "  Swagger: http://localhost/swagger/"
	@echo "  Admin:   http://localhost/admin/"

# ──────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────

.PHONY: help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
