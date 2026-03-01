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

.PHONY: sync-db sync-assets sync-json sync-remote

sync-db: ## Dump remote DB and restore locally
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T db pg_dump -U mediacms -Fc mediacms" > bjj_dump.pgdump
	$(COMPOSE) exec -T db pg_restore -U mediacms -d mediacms --clean --if-exists < bjj_dump.pgdump
	@echo "Database restored. Run 'make migrate' if needed."

sync-assets: ## Download thumbnails + HLS manifests from remote
	$(COMPOSE) exec web python manage.py sync_remote_assets

sync-json: ## Sync techniques.json from remote server
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T web cat files/data/techniques.json" > files/data/techniques.json
	@echo "techniques.json synced from $(REMOTE_HOST)"

sync-remote: sync-db sync-assets sync-json ## Full sync: database + assets + JSON data from remote

# ──────────────────────────────────────────────
# Frontend build
# ──────────────────────────────────────────────

.PHONY: frontend-build

frontend-build: ## Rebuild frontend and copy to static/
	cd frontend && NODE_OPTIONS=--openssl-legacy-provider npm run dist
	cp frontend/dist/static/js/*.js static/js/
	cp frontend/dist/static/js/*.txt static/js/ 2>/dev/null || true
	cp frontend/dist/static/css/*.css static/css/
	@echo "Frontend built and copied to static/"

# ──────────────────────────────────────────────
# Deploy to production
# ──────────────────────────────────────────────

.PHONY: deploy deploy-pull deploy-static deploy-restart deploy-verify

deploy: deploy-pull deploy-static deploy-restart deploy-verify ## Full deploy to production

deploy-pull: ## Pull latest code on production
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && git pull origin main"

deploy-static: ## Ensure frontend/dist/static exists and run collectstatic on production
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && mkdir -p frontend/dist/static && cp -r static/js static/css static/favicons static/images static/lib frontend/dist/static/"
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T web python manage.py collectstatic --noinput"

deploy-restart: ## Restart migrations + web + celery on production
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) restart migrations"
	@sleep 5
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) restart web celery_worker"

deploy-verify: ## Verify production is healthy
	@echo "=== Migration status ==="
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T web python manage.py showmigrations files"
	@echo ""
	@echo "=== HTTP check ==="
	@curl -s -o /dev/null -w "Homepage: %{http_code}\n" -L https://$(REMOTE_HOST)/
	@echo ""
	@echo "Deploy complete."

# ──────────────────────────────────────────────
# Sync DB data to production
# ──────────────────────────────────────────────

.PHONY: push-technique-media

push-technique-media: ## Export local TechniqueMedia records and import to production
	@echo "Exporting TechniqueMedia from local DB..."
	$(COMPOSE) exec -T web python manage.py shell -c "\
from files.models import TechniqueMedia; \
[print(f'{tm.technique_id}|{tm.media.friendly_token}|{tm.title_override or \"\"}') for tm in TechniqueMedia.objects.select_related('media').all()]" > /tmp/technique_media_export.txt
	@echo "Importing $$(wc -l < /tmp/technique_media_export.txt | tr -d ' ') records to production..."
	@cat /tmp/technique_media_export.txt | ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T web python manage.py shell -c \"\
import sys; \
from files.models import TechniqueMedia, Media; \
from users.models import User; \
admin = User.objects.filter(is_superuser=True).first(); \
created = 0; \
for line in sys.stdin: \
    parts = line.strip().split('|'); \
    if len(parts) < 2: continue; \
    tid, token, title = parts[0], parts[1], parts[2] if len(parts) > 2 else ''; \
    try: \
        media = Media.objects.get(friendly_token=token); \
        _, was_created = TechniqueMedia.objects.get_or_create(technique_id=tid, media=media, defaults={'title_override': title, 'added_by': admin}); \
        created += int(was_created); \
    except Media.DoesNotExist: print('Missing: ' + token); \
print(str(created) + ' records created'); \
\""
	@rm /tmp/technique_media_export.txt

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
